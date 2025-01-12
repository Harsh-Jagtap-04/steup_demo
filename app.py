from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pandas as pd
import mysql.connector
import re

app = Flask(__name__)
CORS(app)  # Enable CORS

# MySQL Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "excel_data",
}

# Function to split Test Name
def parse_test_name(test_name):
    level = re.search(r"Level \d+", test_name, re.IGNORECASE)
    attempt = re.search(r"Attempt \d+", test_name, re.IGNORECASE)
    name = re.sub(r"Level \d+|Attempt \d+", "", test_name).strip()

    return {
        "Level": level.group(0) if level else None,
        "Test Name": name,
        "Attempt": attempt.group(0) if attempt else None,
    }

# Endpoint to upload files
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    table_name = request.form["table"]

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Read Excel file
    df = pd.read_excel(file)

    # Parse Test Name if column exists
    if "Test name" in df.columns:
        test_name_parsed = df["Test name"].apply(parse_test_name)
        df = df.drop(columns=["Test name"]).join(pd.DataFrame(test_name_parsed.tolist()))

    # Connect to MySQL and create table
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Generate CREATE TABLE SQL
    columns = ", ".join([f"`{col}` TEXT" for col in df.columns])
    create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
    cursor.execute(create_table_sql)

    # Insert data
    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(row))
        insert_sql = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
        cursor.execute(insert_sql, tuple(row))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"File uploaded and data stored in {table_name}"}), 200

@app.route("/dashboard", methods=["GET"])
def get_dashboard_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    query = """
    WITH levels AS (
        SELECT 'Level 1' AS level UNION ALL
        SELECT 'Level 2' UNION ALL
        SELECT 'Level 3' UNION ALL
        SELECT 'Level 4' UNION ALL
        SELECT 'Level 5'
    )
    SELECT 
        b.batch AS batch,
        l.level AS level,
        COUNT(DISTINCT t.`Email`) AS invites,
        SUM(CASE WHEN t.`Test status` = 'Cleared CutOff' THEN 1 ELSE 0 END) AS cleared,
        SUM(CASE 
            WHEN t.`Test status` = 'Failed CutOff' AND t.`Attempt` = 'Attempt 3' THEN 1
            WHEN t.`Test status` = 'Not Appeared' AND t.`Attempt` = 'Attempt 3' THEN 1
            ELSE 0
        END) AS failed,
        SUM(CASE 
            WHEN t.`Test status` = 'In Progress' AND (t.`Attempt` = 'Attempt 1' OR t.`Attempt` = 'Attempt 2') THEN 1
            ELSE 0
        END) AS in_progress
    FROM levels AS l
    LEFT JOIN testtable AS t ON l.level = t.`Level`
    LEFT JOIN batchinformation AS b ON t.`Email` = b.`Email`
    GROUP BY b.batch, l.level
    ORDER BY b.batch, l.level;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Reshape results into a tabular format
    table_data = {}
    batches = set()
    for row in results:
        level = row["level"]
        batch = row["batch"] or "Unspecified Batch"
        batches.add(batch)

        if level not in table_data:
            table_data[level] = {}

        table_data[level][batch] = {
            "invites": row["invites"],
            "cleared": row["cleared"],
            "failed": row["failed"],
            "in_progress": row["in_progress"]
        }

    # Ensure all levels (Level 1 to Level 5) are present
    for level in [f"Level {i}" for i in range(1, 6)]:
        if level not in table_data:
            table_data[level] = {}
        for batch in batches:
            if batch not in table_data[level]:
                table_data[level][batch] = {
                    "invites": 0,
                    "cleared": 0,
                    "failed": 0,
                    "in_progress": 0
                }

    cursor.close()
    conn.close()

    # Return as JSON for rendering
    return jsonify({"batches": sorted(list(batches)), "table_data": table_data})

if __name__ == "__main__":
    app.run(debug=True)