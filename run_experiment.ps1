param(
    [string]$Name = "experiment"
)

Write-Host "=== Running attacker.py for experiment: $Name ==="

# Running the attacker
python attacker.py

# Checks if attempts.log was created and rename it with the experiment name and timestamp
if (Test-Path "attempts.log") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $newName = "logs\attempts_$Name`_$timestamp.log"

    Write-Host "Saving log as $newName"
    Move-Item -Force "attempts.log" $newName
}
else {
    Write-Host "ERROR: attempts.log not found!"
}