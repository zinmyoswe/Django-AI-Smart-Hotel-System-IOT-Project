Write-Output "Starting power_agent.py to publish all meters..."

# Run Python script once; it will handle all 6 meters internally
python "agents\power_agent.py"

Write-Output "Finished publishing all meters for all datetimes."
