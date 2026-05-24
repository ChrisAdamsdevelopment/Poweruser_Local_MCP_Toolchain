$TaskName = "SystemAgentMCP"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"
$ScriptPath = Join-Path $PSScriptRoot "start_agent.bat"

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -Command \"& '$ScriptPath'\""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet
$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings

Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

$registered = Get-ScheduledTask -TaskName $TaskName
$nextRun = (Get-ScheduledTaskInfo -TaskName $TaskName).NextRunTime
Write-Host "Task registered: $($registered.TaskName)"
Write-Host "Next scheduled run: $nextRun"
