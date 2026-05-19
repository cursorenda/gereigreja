Add-Type -AssemblyName System.Drawing
$width = 1200
$height = 630
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias
$bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(250, 252, 255))
$g.FillRectangle($bgBrush, 0, 0, $width, $height)
$bluePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(40, 0, 123, 255), 2)
$greenPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(40, 40, 167, 69), 2)
$yellowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(30, 255, 193, 7))
$g.FillEllipse($yellowBrush, 1000, -50, 300, 300)
$g.DrawEllipse($bluePen, -100, 400, 400, 400)
$g.DrawRectangle($greenPen, 900, 400, 150, 150)
$cardRect = New-Object System.Drawing.Rectangle(200, 150, 800, 330)
$shadowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(15, 0, 0, 0))
$g.FillRectangle($shadowBrush, 205, 155, 800, 330)
$whiteBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$g.FillRectangle($whiteBrush, $cardRect)
$titleFont = New-Object System.Drawing.Font("Arial", 80, [System.Drawing.FontStyle]::Bold)
$subtitleFont = New-Object System.Drawing.Font("Arial", 30, [System.Drawing.FontStyle]::Regular)
$footerFont = New-Object System.Drawing.Font("Arial", 18, [System.Drawing.FontStyle]::Italic)
$titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(33, 37, 41))
$subtitleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(108, 117, 125))
$g.DrawString("Gereigreja", $titleFont, $titleBrush, 310, 200)
$g.DrawString("Gestão inteligente para igrejas", $subtitleFont, $subtitleBrush, 290, 320)
$g.DrawString("Secretaria • Financeiro • Agenda • Comunicação", $footerFont, $subtitleBrush, 320, 420)
if (-not (Test-Path "static\img")) { New-Item -ItemType Directory -Path "static\img" -Force }
$filePath = Join-Path (Get-Location) "static\img\gereigreja_og_image.png"
$bmp.Save($filePath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
$file = Get-Item $filePath
Write-Host "File created: $($file.FullName)"
Write-Host "File size: $([math]::Round($file.Length / 1KB, 2)) KB"
