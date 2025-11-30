
from flask import Flask, render_template_string, request, redirect, send_file, flash, url_for
import threading
import time
import io
from controller import registered_nodes, file_locations

app = Flask(__name__)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Storage Dashboard</title>
    <style>
        :root {
            --primary: #4361ee;
            --primary-dark: #3a56d4;
            --danger: #f72585;
            --success: #4cc9f0;
            --light: #f8f9fa;
            --dark: #212529;
            --gray: #6c757d;
            --border: #dee2e6;
        }

        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            color: var(--dark);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .header h1 {
            color: var(--primary);
            font-size: 2.5rem;
            margin-bottom: 8px;
            margin-top: 0;
        }

        .header p {
            color: var(--gray);
            font-size: 1.1rem;
            margin: 0;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary);
            display: block;
        }

        .stat-label {
            color: var(--gray);
            font-size: 0.9rem;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .card h3 {
            color: var(--primary);
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card h3::before {
            content: "📁";
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        label {
            font-weight: 500;
            margin-bottom: 6px;
            color: var(--dark);
        }

        input, select {
            padding: 12px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.2s ease;
        }

        input:focus {
            outline: none;
            border-color: var(--primary);
        }

        .btn { 
            background: var(--primary); 
            color: #fff; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .btn:hover { 
            background: var(--primary-dark);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .table-container {
            overflow-x: auto;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        table { 
            border-collapse: collapse; 
            width: 100%; 
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }

        th, td { 
            border: 1px solid var(--border); 
            padding: 12px; 
            text-align: left; 
        }

        th { 
            background: var(--primary);
            color: white;
            font-weight: 600;
        }

        tr:nth-child(even) {
            background: #f8f9fa;
        }

        tr:hover {
            background: #e9ecef;
        }

        .online { 
            color: #065f46;
            font-weight: bold;
            background: #d1fae5;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }

        .offline { 
            color: #991b1b;
            font-weight: bold;
            background: #fee2e2;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
        }

        .msg { 
            color: #d32f2f; 
            font-weight: bold; 
            margin: 10px;
            background: #fee2e2;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #fecaca;
        }

        .owner-tag {
            display: inline-block;
            background: #e0e7ff;
            color: var(--primary);
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            margin: 2px;
            font-weight: 500;
        }

        @media (max-width: 768px) {
            .form-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            body {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Distributed Storage Dashboard</h1>
            <p>Monitor and manage your distributed storage network</p>
        </div>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="msg">{{ messages[0] }}</div>
            {% endif %}
        {% endwith %}

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{{ nodes|length }}</span>
                <span class="stat-label">Total Nodes</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ nodes.values()|selectattr("2")|list|length }}</span>
                <span class="stat-label">Online Nodes</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ files|length }}</span>
                <span class="stat-label">Total Files</span>
            </div>
        </div>

        <div class="card">
            <h3>Register Node</h3>
            <form method="post" action="/register_node">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Node ID:</label>
                        <input name="node_id" required placeholder="Enter node identifier">
                    </div>
                    <div class="form-group">
                        <label>Address:</label>
                        <input name="address" value="127.0.0.1" required>
                    </div>
                    <div class="form-group">
                        <label>Port:</label>
                        <input name="port" type="number" value="5001" required>
                    </div>
                </div>
                <button class="btn" type="submit">Register Node</button>
            </form>
        </div>

        <div class="card">
            <h3>Upload File</h3>
            <form method="post" action="/upload_file" enctype="multipart/form-data">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Filename:</label>
                        <input name="filename" required placeholder="Enter filename">
                    </div>
                    <div class="form-group">
                        <label>Owner Node ID:</label>
                        <input name="owner_id" required placeholder="Enter owner node ID">
                    </div>
                    <div class="form-group">
                        <label>File Data:</label>
                        <input type="file" name="filedata" required style="padding: 8px;">
                    </div>
                </div>
                <button class="btn" type="submit">Upload File</button>
            </form>
        </div>

        <div class="card">
            <h3>Download File</h3>
            <form method="get" action="/download_file">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Filename:</label>
                        <input name="filename" required placeholder="Enter filename to download">
                    </div>
                </div>
                <button class="btn" type="submit">Download File</button>
            </form>
        </div>

        <div class="card">
            <h3>📊 Node Status</h3>
            <div class="table-container">
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Address</th>
                        <th>Port</th>
                        <th>Status</th>
                        <th>Last Seen</th>
                    </tr>
                    {% for nid, (addr, port, online, last_seen) in nodes.items() %}
                    <tr>
                        <td><strong>{{ nid }}</strong></td>
                        <td>{{ addr }}</td>
                        <td>{{ port }}</td>
                        <td>
                            <span class="{{ 'online' if online else 'offline' }}">
                                {{ '🟢 Online' if online else '🔴 Offline' }}
                            </span>
                        </td>
                        <td>{{ last_seen }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <div class="card">
            <h3>🗂️ File Registry</h3>
            <div class="table-container">
                <table>
                    <tr>
                        <th>Filename</th>
                        <th>Owners</th>
                        <th>Upload Time</th>
                    </tr>
                    {% for fname, info in files.items() %}
                    <tr>
                        <td><strong>{{ fname }}</strong></td>
                        <td>
                            {% for owner in info['owners'] %}
                                <span class="owner-tag">{{ owner[0] }} ({{ owner[1] }}:{{ owner[2] }})</span>
                            {% endfor %}
                        </td>
                        <td>{{ info['upload_time'] }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(TEMPLATE, nodes=registered_nodes, files=file_locations)


# --- Web endpoints for actions ---
@app.route('/register_node', methods=['POST'])
def register_node():
    node_id = request.form['node_id']
    address = request.form['address']
    port = int(request.form['port'])
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    registered_nodes[node_id] = (address, port, True, now)
    flash(f"Node {node_id} registered at {address}:{port} (ONLINE)")
    return redirect(url_for('dashboard'))

@app.route('/upload_file', methods=['POST'])
def upload_file():
    filename = request.form['filename']
    owner_id = request.form['owner_id']
    file = request.files['filedata']
    if not file:
        flash("No file uploaded!")
        return redirect(url_for('dashboard'))
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    # Simulate file storage: just record metadata
    if filename not in file_locations:
        file_locations[filename] = {'owners': set(), 'upload_time': now}
    # Use dummy address/port if owner not registered
    if owner_id in registered_nodes:
        addr, port, _, _ = registered_nodes[owner_id]
    else:
        addr, port = '127.0.0.1', 5001
    file_locations[filename]['owners'].add((owner_id, addr, port))
    file_locations[filename]['upload_time'] = now
    flash(f"File '{filename}' uploaded and owned by {owner_id}")
    return redirect(url_for('dashboard'))

@app.route('/download_file', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if filename not in file_locations:
        flash(f"File '{filename}' not found!")
        return redirect(url_for('dashboard'))
    # Simulate file content
    content = f"Dummy content of {filename} (not actual file data)"
    return send_file(io.BytesIO(content.encode()), as_attachment=True, download_name=filename)

def run_dashboard():
    app.secret_key = 'zebcontrollersecret'
    app.run(port=8080, debug=False, use_reloader=False)

# To run the dashboard in parallel with the controller, call run_dashboard() in a thread.
