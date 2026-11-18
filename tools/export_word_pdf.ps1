param(
    [string]$DocxPath = (Join-Path $PSScriptRoot '..\docs\Evidencias_Bookshelf.docx'),
    [string]$PdfPath = (Join-Path $PSScriptRoot '..\docs\Evidencias_Bookshelf.pdf')
)
$ErrorActionPreference = 'Stop'
$documentPath = (Resolve-Path -LiteralPath $DocxPath).Path
$outputPath = [System.IO.Path]::GetFullPath($PdfPath)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $document = $word.Documents.Open($documentPath, $false, $true)
    $document.ExportAsFixedFormat($outputPath, 17)
    $document.Close(0)
    Write-Output $outputPath
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
