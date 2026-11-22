# Sign the Play bundle with your upload key.
#
# Why this exists: the GitHub build has no copy of your upload keystore, so the bundle it produces is
# signed with the test key that lives in the repository for emulator runs. Play checks the upload
# certificate and rejects anything else. This script replaces that signature with yours.
#
# Your keystore password is typed here, into jarsigner, on this machine. It is not stored, not echoed,
# and does not go anywhere else.
#
# Run it from PowerShell in your Downloads folder:
#
#     powershell -ExecutionPolicy Bypass -File .\sign-aab-with-upload-key.ps1 `
#         -Aab .\app-play-release.aab `
#         -Keystore C:\path\to\gaurav-jyotish-upload.jks `
#         -Alias <your key alias>
#
# It writes app-play-release-upload-signed.aab beside the input and prints the certificate it used, so
# you can check it against App integrity -> App signing in Play Console before uploading.

param(
    [Parameter(Mandatory = $true)] [string] $Aab,
    [Parameter(Mandatory = $true)] [string] $Keystore,
    [Parameter(Mandatory = $true)] [string] $Alias
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Find-Tool([string] $name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $roots = @()
    if ($env:JAVA_HOME) { $roots += Join-Path $env:JAVA_HOME 'bin' }
    $roots += "$env:ProgramFiles\Android\Android Studio\jbr\bin"
    $roots += "$env:LOCALAPPDATA\Programs\Android Studio\jbr\bin"
    $roots += "$env:ProgramFiles\Java\*\bin"
    foreach ($r in $roots) {
        $hit = Get-ChildItem -Path (Join-Path $r "$name.exe") -ErrorAction SilentlyContinue |
               Select-Object -First 1
        if ($hit) { return $hit.FullName }
    }
    throw "Could not find $name.exe. Install a JDK, or set JAVA_HOME to one, and run this again."
}

$jarsigner = Find-Tool 'jarsigner'
$keytool   = Find-Tool 'keytool'

$Aab      = (Resolve-Path $Aab).Path
$Keystore = (Resolve-Path $Keystore).Path
$out      = Join-Path (Split-Path $Aab) ((Split-Path $Aab -Leaf) -replace '\.aab$', '-upload-signed.aab')

# jarsigner adds a signature rather than replacing one, and a bundle carrying two signatures is not a
# bundle Play will take. So copy the input without its existing signature block first.
Write-Host "Removing the old signature..."
if (Test-Path $out) { Remove-Item $out }
Copy-Item $Aab $out
$zip = [System.IO.Compression.ZipFile]::Open($out, 'Update')
try {
    $stale = @($zip.Entries | Where-Object {
        $_.FullName -match '^META-INF/[^/]+\.(SF|RSA|DSA|EC)$' -or $_.FullName -eq 'META-INF/MANIFEST.MF'
    })
    foreach ($e in $stale) { Write-Host "  dropping $($e.FullName)"; $e.Delete() }
    if ($stale.Count -eq 0) { Write-Host "  (none found - the bundle was unsigned)" }
} finally {
    $zip.Dispose()
}

Write-Host ""
Write-Host "Signing with $Alias from $Keystore."
Write-Host "jarsigner will ask for the keystore password. Nothing records what you type."
Write-Host ""
& $jarsigner -digestalg SHA-256 -sigalg SHA256withRSA -keystore $Keystore $out $Alias
if ($LASTEXITCODE -ne 0) { throw "jarsigner failed with exit code $LASTEXITCODE. The bundle at $out is not usable; delete it and try again." }

Write-Host ""
Write-Host "Verifying..."
# Capture first, filter after. Cutting a native command's pipeline short with Select-Object -First can
# kill the process mid-write and report a failure that never happened.
$verify = & $jarsigner -verify -verbose:summary -certs $out 2>&1
if ($LASTEXITCODE -ne 0) {
    $verify | Write-Host
    throw "Verification failed. The bundle at $out is not usable."
}
$verify | Where-Object { $_ -match 'jar verified|CN=' } | Select-Object -Unique | Write-Host

Write-Host ""
Write-Host "The certificate this bundle now carries:"
$cert = & $keytool -list -v -keystore $Keystore -alias $Alias 2>&1
$cert | Where-Object { $_ -match 'Owner:|SHA256:' } | Write-Host

Write-Host ""
Write-Host "Done: $out"
Write-Host "Check that SHA256 against Play Console -> App integrity -> App signing -> Upload key certificate."
Write-Host "If they match, that file is the one to upload to the Production track."
