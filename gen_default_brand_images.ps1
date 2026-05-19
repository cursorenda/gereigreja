Add-Type -AssemblyName System.Drawing

function Create-Image {
    param(
        [string]$Path,
        [string]$Title,
        [string]$Subtitle,
        [System.Drawing.Color]$BgColor,
        [System.Drawing.Color]$AccentColor
    )
    
    $width = 1200
    $height = 630
    $bmp = New-Object System.Drawing.Bitmap($width, $height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    
    # Background
    $rect = New-Object System.Drawing.Rectangle(0, 0, $width, $height)
    $bgBrush = New-Object System.Drawing.SolidBrush($BgColor)
    $g.FillRectangle($bgBrush, $rect)
    
    # Accents (soft geometric)
    $accentBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(40, $AccentColor))
    $g.FillEllipse($accentBrush, -100, -100, 400, 400)
    $g.FillEllipse($accentBrush, [int]($width - 300), [int]($height - 300), 500, 500)
    
    # Fonts
    $titleFont = New-Object System.Drawing.Font("Segoe UI", 60, [System.Drawing.FontStyle]::Bold)
    $subFont = New-Object System.Drawing.Font("Segoe UI", 30)
    $footerFont = New-Object System.Drawing.Font("Segoe UI", 20, [System.Drawing.FontStyle]::Italic)
    $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(50, 50, 50))
    $footerBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Gray)
    
    # Text Drawing
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    
    $midWidth = [float]$width
    $midHeight = [float]$height
    
    $titleRect = New-Object System.Drawing.RectangleF(0, ($midHeight / 2 - 60), $midWidth, 80)
    $subRect = New-Object System.Drawing.RectangleF(0, ($midHeight / 2 + 40), $midWidth, 50)
    $footerRect = New-Object System.Drawing.RectangleF(0, ($midHeight - 60), $midWidth, 40)
    
    $g.DrawString($Title, $titleFont, $textBrush, $titleRect, $format)
    $g.DrawString($Subtitle, $subFont, $textBrush, $subRect, $format)
    $g.DrawString("Gereigreja", $footerFont, $footerBrush, $footerRect, $format)
    
    # Cleanup and Save
    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
}

if (-not (Test-Path "static\img")) { New-Item -ItemType Directory -Path "static\img" -Force }

Create-Image -Path "static\img\default_ministerio.png" -Title "Ministério" -Subtitle "Imagem padrão institucional" -BgColor ([System.Drawing.Color]::GhostWhite) -AccentColor ([System.Drawing.Color]::CornflowerBlue)
Create-Image -Path "static\img\default_igreja.png" -Title "Igreja" -Subtitle "Imagem padrão da congregação" -BgColor ([System.Drawing.Color]::FromArgb(250, 255, 250)) -AccentColor ([System.Drawing.Color]::SeaGreen)

Get-ChildItem "static\img\default_ministerio.png", "static\img\default_igreja.png" | Select-Object FullName, @{Name="Size(KB)"; Expression={"{0:N2}" -f ($_.Length / 1KB)}}
