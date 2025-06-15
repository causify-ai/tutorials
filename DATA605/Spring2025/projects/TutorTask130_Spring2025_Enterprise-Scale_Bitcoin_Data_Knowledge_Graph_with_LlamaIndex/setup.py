#!/usr/bin/env python3
import os
import subprocess
import time
import requests
import json
import shutil
import sys

def run_command(command):
    print(f"Running: {command}")
    return subprocess.run(command, shell=True, check=True)

def setup_neo4j():
    # Check if neo4j is already running
    result = subprocess.run("docker ps -q -f name=neo4j-apoc", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Neo4j is already running")
        return
    
    # Check if container exists but is stopped
    result = subprocess.run("docker ps -aq -f name=neo4j-apoc", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Starting existing Neo4j container")
        run_command("docker start neo4j-apoc")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("plugins", exist_ok=True)
    
    # Run Neo4j container
    run_command("""
    docker run -d \
    -p 7474:7474 -p 7687:7687 \
    -v $PWD/data:/data -v $PWD/plugins:/plugins \
    --name neo4j-apoc \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4JLABS_PLUGINS='["apoc"]' \
    neo4j:latest
    """)
    
    print("Neo4j is now running")

def setup_prometheus():
    # Create prometheus config directory in current working directory
    config_dir = os.path.join(os.getcwd(), "prometheus")
    os.makedirs(config_dir, exist_ok=True)
    
    # Create prometheus.yml config file
    config_file = os.path.join(config_dir, "prometheus.yml")
    try:
        with open(config_file, "w") as f:
            f.write("""
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bitcoin-kg'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
            """)
        print(f"Created Prometheus config at {config_file}")
    except PermissionError:
        # Try using a different directory if we don't have permission
        alt_config_dir = os.path.join(os.path.expanduser("~"), "prometheus_config")
        os.makedirs(alt_config_dir, exist_ok=True)
        alt_config_file = os.path.join(alt_config_dir, "prometheus.yml")
        
        try:
            with open(alt_config_file, "w") as f:
                f.write("""
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bitcoin-kg'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
                """)
            print(f"Created Prometheus config at {alt_config_file}")
            config_dir = alt_config_dir
            config_file = alt_config_file
        except PermissionError:
            print(f"Permission denied when writing to {alt_config_file}")
            print("Try running with sudo or check directory permissions")
            return False
    
    # Check if prometheus is already running
    result = subprocess.run("docker ps -q -f name=prometheus", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Prometheus is already running, stopping it to apply new configuration")
        run_command("docker stop prometheus")
        run_command("docker rm prometheus")
    else:
        # Check if container exists but is stopped
        result = subprocess.run("docker ps -aq -f name=prometheus", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print("Removing existing Prometheus container")
            run_command("docker rm prometheus")
    
    # Run Prometheus container with host network
    config_mount = f"{config_dir}:/etc/prometheus"
    cmd = f"""
    docker run -d \
    --network host \
    -v {config_mount} \
    --name prometheus \
    prom/prometheus
    """
    try:
        run_command(cmd)
        print("Prometheus is now running with host network mode")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Prometheus: {e}")
        return False

def setup_grafana():
    # Create grafana config and provisioning directories
    base_dir = os.getcwd()
    grafana_dir = os.path.join(base_dir, "grafana")
    datasources_dir = os.path.join(grafana_dir, "provisioning", "datasources")
    dashboards_dir = os.path.join(grafana_dir, "provisioning", "dashboards")
    dash_storage_dir = os.path.join(grafana_dir, "dashboards")
    
    # Create all directories
    os.makedirs(datasources_dir, exist_ok=True)
    os.makedirs(dashboards_dir, exist_ok=True)
    os.makedirs(dash_storage_dir, exist_ok=True)
    
    # Create prometheus datasource config
    ds_config = os.path.join(datasources_dir, "prometheus.yml")
    try:
        with open(ds_config, "w") as f:
            f.write("""
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: false
            """)
        print(f"Created Grafana datasource config at {ds_config}")
    except PermissionError:
        print(f"Permission denied when writing to {ds_config}")
        print("Try running with sudo or check directory permissions")
        return
    
    # Create dashboard config
    dash_config = os.path.join(dashboards_dir, "bitcoin-kg.yml")
    try:
        with open(dash_config, "w") as f:
            f.write("""
apiVersion: 1

providers:
  - name: 'Bitcoin KG'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
            """)
        print(f"Created Grafana dashboard config at {dash_config}")
    except PermissionError:
        print(f"Permission denied when writing to {dash_config}")
        print("Try running with sudo or check directory permissions")
        return
    
    # Create dashboard file
    dash_file = os.path.join(dash_storage_dir, "bitcoin-kg.json")
    try:
        with open(dash_file, "w") as f:
            f.write("""
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "rate(bitcoin_kg_query_duration_seconds_sum[5m]) / rate(bitcoin_kg_query_duration_seconds_count[5m])",
          "refId": "A"
        }
      ],
      "title": "Query Response Time",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "rate(bitcoin_kg_query_total[1m])",
          "refId": "A"
        }
      ],
      "title": "Requests Per Second",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 6,
        "x": 0,
        "y": 8
      },
      "id": 3,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "9.3.0",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "bitcoin_kg_query_total",
          "refId": "A"
        }
      ],
      "title": "Total Queries",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 6,
        "x": 6,
        "y": 8
      },
      "id": 4,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "9.3.0",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "bitcoin_kg_updates_total",
          "refId": "A"
        }
      ],
      "title": "Knowledge Graph Updates",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 6,
        "x": 12,
        "y": 8
      },
      "id": 5,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "9.3.0",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "bitcoin_kg_node_count",
          "refId": "A"
        }
      ],
      "title": "Node Count",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 6,
        "x": 18,
        "y": 8
      },
      "id": 6,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "9.3.0",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "bitcoin_kg_relation_count",
          "refId": "A"
        }
      ],
      "title": "Relation Count",
      "type": "stat"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Bitcoin Knowledge Graph",
  "uid": "bitcoin-kg",
  "version": 1,
  "weekStart": ""
}
            """)
        print(f"Created Grafana dashboard at {dash_file}")
    except PermissionError:
        print(f"Permission denied when writing to {dash_file}")
        print("Try running with sudo or check directory permissions")
        return
    
    # Check if grafana is already running
    result = subprocess.run("docker ps -q -f name=grafana", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Grafana is already running")
        return
    
    # Check if container exists but is stopped
    result = subprocess.run("docker ps -aq -f name=grafana", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("Starting existing Grafana container")
        run_command("docker start grafana")
        return
    
    # Run Grafana container with host.docker.internal instead of linking to prometheus
    prov_mount = f"{os.path.join(grafana_dir, 'provisioning')}:/etc/grafana/provisioning"
    dash_mount = f"{dash_storage_dir}:/var/lib/grafana/dashboards"
    
    # Run Grafana container with host network
    cmd = f"""
    docker run -d \
    --network host \
    -v {prov_mount} \
    -v {dash_mount} \
    --name grafana \
    grafana/grafana
    """
    run_command(cmd)
    
    print("Grafana is now running")

def main():
    print("Setting up Bitcoin Knowledge Graph monitoring...")
    
    setup_neo4j()
    
    # First try to set up Prometheus
    prometheus_running = setup_prometheus()
    
    # Only proceed with Grafana if Prometheus was successful or we're ignoring it
    if prometheus_running:
        setup_grafana()
    else:
        print("\nWarning: Skipping Grafana setup as Prometheus setup failed.")
        print("You can run this script again with only Grafana by modifying the main() function.")
    
    print("\nSetup complete!")
    
    if prometheus_running:
        print("Prometheus: http://localhost:9090")
        print("Grafana: http://localhost:3000 (admin/admin)")
    
    print("Neo4j: http://localhost:7474 (if you set it up)")
    print("\nDon't forget to add Prometheus metrics to your application code!")

if __name__ == "__main__":
    main()