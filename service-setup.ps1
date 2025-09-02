# Absoluter Pfad zum aktuellen Skriptordner holen
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Variablen
$nssmPath = Join-Path $scriptDir "nssm.exe"
$serviceName = "hikdev-svc"
$exePath = Join-Path $scriptDir "HikDev.exe"
$workingDirectory = $scriptDir

# Dienst installieren
& $nssmPath install $serviceName $exePath
& $nssmPath set $serviceName AppDirectory $workingDirectory

# Dienst starten
& $nssmPath start $serviceName

