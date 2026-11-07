param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$outDir = $PSScriptRoot
$qaDir = Join-Path $env:TEMP 'college_darpan_appendix_qa'
New-Item -ItemType Directory -Path $qaDir -Force | Out-Null

$pages = @(
    @{ Title='Application setup and configuration'; Sections=@(
        @{ File='app.py'; Start=1; End=45; Note='Flask imports, app setup, startup preparation, and shared template values.' },
        @{ File='config.py'; Start=1; End=28; Note='Runtime configuration and default recommendation weights.' }
    )},
    @{ Title='Recommendation request validation'; Sections=@(
        @{ File='app.py'; Start=47; End=91; Note='Preference category, exam, rank, budget, branch, and management validation.' },
        @{ File='app.py'; Start=93; End=119; Note='Recommendation weight input validation. The parsed preference return object is omitted.' }
    )},
    @{ Title='Comparison identifiers and homepage route'; Sections=@(
        @{ File='app.py'; Start=134; End=189; Note='College ID parsing, comparison session validation, response data, and homepage route.' }
    )},
    @{ Title='Directory and college detail routes'; Sections=@(
        @{ File='app.py'; Start=191; End=248; Note='Directory query parameters, service call, and template context.' },
        @{ File='app.py'; Start=364; End=372; Note='Detail lookup and handling when a college record is missing.' }
    )},
    @{ Title='Recommendation and comparison routes'; Sections=@(
        @{ File='app.py'; Start=374; End=421; Note='Recommendation form processing and comparison page route.' },
        @{ File='app.py'; Start=517; End=545; Note='Comparison API read and add actions. Later remove, clear, and set branches are omitted.' }
    )},
    @{ Title='SQLite access and database schema'; Sections=@(
        @{ File='database/db.py'; Start=1; End=48; Note='Connection, parameterized query, write, and SQL script helpers.' },
        @{ File='database/schema.sql'; Start=14; End=33; Note='Excerpt from the colleges table definition; other tables and indexes are omitted.' }
    )},
    @{ Title='College search and filters'; Sections=@(
        @{ File='services/college_service.py'; Start=70; End=145; Note='College selection query and parameterized category, management, text, district, institution, and branch filters. Later filter and sorting sections are omitted.' }
    )},
    @{ Title='Recommendation scoring'; Sections=@(
        @{ File='services/recommendation_engine.py'; Start=41; End=112; Note='Weight normalization, branch compatibility, and affordability scoring. Other scoring functions are omitted.' }
    )},
    @{ Title='Admission safeguards and weighted ranking'; Sections=@(
        @{ File='services/recommendation_engine.py'; Start=168; End=195; Note='Historical cutoff query and matching inputs.' },
        @{ File='services/recommendation_engine.py'; Start=205; End=213; Note='Favorable historical cutoff case. Borderline and competitive branches are omitted.' },
        @{ File='services/recommendation_engine.py'; Start=341; End=352; Note='Weighted match score and admission safeguard call from the recommendation pipeline.' },
        @{ File='tests/test_recommendations.py'; Start=69; End=73; Note='Existing regression test for missing admission inputs; this appendix does not claim the test was run.' }
    )},
    @{ Title='Chatbot intent handling and comparison response'; Sections=@(
        @{ File='services/chatbot_service.py'; Start=154; End=197; Note='Local message handling and initial intent routing rules; other intent branches are omitted.' },
        @{ File='services/chatbot_service.py'; Start=242; End=264; Note='Database-backed college comparison lookup and insufficient-record response.' }
    )},
    @{ Title='Homepage, directory, recommendation, and comparison templates'; Sections=@(
        @{ File='templates/index.html'; Start=13; End=18; Note='Homepage headline and introductory content.' },
        @{ File='templates/colleges.html'; Start=53; End=63; Note='Directory GET filter form and education category selector; remaining filters are omitted.' },
        @{ File='templates/recommendations.html'; Start=33; End=44; Note='Recommendation category controls.' },
        @{ File='templates/compare.html'; Start=17; End=31; Note='Comparison page college selector.' }
    )},
    @{ Title='Recommendation, comparison, and browser interactions'; Sections=@(
        @{ File='static/js/main.js'; Start=43; End=54; Note='Client request wrapper for the session-backed comparison API.' },
        @{ File='static/js/compare.js'; Start=5; End=19; Note='Comparison page add/remove actions.' },
        @{ File='static/js/recommendations.js'; Start=6; End=19; Note='Beginning of the category-aware option configuration; remaining options are omitted.' },
        @{ File='static/js/chatbot.js'; Start=190; End=208; Note='Chat message request and response/error handling.' }
    )}
)

if ($pages.Count -ne 12) { throw "Expected 12 page definitions, found $($pages.Count)." }

function Get-SectionLines($section) {
    $path = Join-Path $root $section.File
    if (-not (Test-Path -LiteralPath $path)) { throw "Source file not found: $($section.File)" }
    $lines = [System.IO.File]::ReadAllLines($path, [System.Text.Encoding]::UTF8)
    if ($section.Start -lt 1 -or $section.End -gt $lines.Length) { throw "Invalid range for $($section.File): $($section.Start)-$($section.End)" }
    return ,$lines[($section.Start - 1)..($section.End - 1)]
}

function Escape-Xml([string]$text) { return [System.Security.SecurityElement]::Escape($text) }

function New-CodeParagraph([string]$text) {
    if ($text.Length -eq 0) { return '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="80" w:lineRule="exact"/></w:pPr></w:p>' }
    $safe = Escape-Xml $text
    return "<w:p><w:pPr><w:spacing w:before=`"0`" w:after=`"0`" w:line=`"180`" w:lineRule=`"exact`"/><w:keepLines/></w:pPr><w:r><w:rPr><w:rFonts w:ascii=`"Consolas`" w:hAnsi=`"Consolas`" w:eastAsia=`"Consolas`"/><w:sz w:val=`"17`"/><w:szCs w:val=`"17`"/></w:rPr><w:t xml:space=`"preserve`">$safe</w:t></w:r></w:p>"
}

function New-LabelParagraph([string]$text, [string]$style='') {
    $safe = Escape-Xml $text
    $pageBreak = if ($style -eq 'pagebreak') { '<w:pageBreakBefore/>' } else { '' }
    $fontSize = if ($style -eq 'section') { '18' } elseif ($style -eq 'note') { '14' } else { '30' }
    $color = if ($style -eq 'note') { '64748B' } elseif ($style -eq 'section') { '4C3A63' } else { '1E293B' }
    $bold = if ($style -eq 'note') { '' } else { '<w:b/>' }
    $after = if ($style -eq 'note') { '50' } elseif ($style -eq 'section') { '40' } else { '100' }
    return "<w:p><w:pPr>$pageBreak<w:spacing w:before=`"0`" w:after=`"$after`"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii=`"Arial`" w:hAnsi=`"Arial`"/><w:color w:val=`"$color`"/>$bold<w:sz w:val=`"$fontSize`"/></w:rPr><w:t xml:space=`"preserve`">$safe</w:t></w:r></w:p>"
}

# Draw PDF pages as high-resolution A4 page images so the selected Consolas code
# and Unicode characters remain visually consistent in print.
Add-Type -AssemblyName System.Drawing
$fontCollection = [System.Drawing.Text.PrivateFontCollection]::new()
$fontCollection.AddFontFile('C:\Windows\Fonts\consola.ttf')
$codeFont = [System.Drawing.Font]::new($fontCollection.Families[0], 8.5, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Point)
$smallFont = [System.Drawing.Font]::new('Arial', 7.0, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Point)
$sectionFont = [System.Drawing.Font]::new('Arial', 9.0, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
$titleFont = [System.Drawing.Font]::new('Arial', 15.0, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
$noteFont = [System.Drawing.Font]::new('Arial', 7.0, [System.Drawing.FontStyle]::Italic, [System.Drawing.GraphicsUnit]::Point)
$darkBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(30,41,59))
$codeBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(17,24,39))
$mutedBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(100,116,139))
$accentBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(96,70,127))
$a4Width = 595.28
$a4Height = 841.89
$pagesPng = @()
$pageXml = @()

for ($i = 0; $i -lt $pages.Count; $i++) {
    $page = $pages[$i]
    $bitmap = [System.Drawing.Bitmap]::new(2480, 3508)
    $bitmap.SetResolution(300, 300)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.PageUnit = [System.Drawing.GraphicsUnit]::Point
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::White)
    $x = 38.0
    $y = 36.0
    $graphics.DrawString("COLLEGE DARPAN  |  CODE APPENDIX  |  PAGE $($i + 1) OF 12", $smallFont, $mutedBrush, $x, $y)
    $y += 15
    $graphics.DrawString($page.Title, $titleFont, $darkBrush, $x, $y)
    $y += 24
    if ($i -eq 0) {
        $graphics.DrawString('Selected implementation excerpts from the existing project. Each excerpt is labeled; omitted source sections are not represented as complete code.', $smallFont, $mutedBrush, $x, $y)
        $y += 16
    }
    foreach ($section in $page.Sections) {
        $sectionTitle = "$($section.File)  (lines $($section.Start)-$($section.End))"
        $graphics.DrawString($sectionTitle, $sectionFont, $accentBrush, $x, $y)
        $y += 12
        $note = $section.Note
        $graphics.DrawString($note, $noteFont, $mutedBrush, $x, $y, [System.Drawing.StringFormat]::GenericTypographic)
        $y += 10
        $sourceLines = Get-SectionLines $section
        foreach ($sourceLine in $sourceLines) {
            if ([string]::IsNullOrWhiteSpace($sourceLine)) { $y += 3.0; continue }
            $remaining = $sourceLine
            $continuation = $false
            while ($remaining.Length -gt 0) {
                $prefix = if ($continuation) { '    ' } else { '' }
                $maxChars = 98 - $prefix.Length
                if ($remaining.Length -le $maxChars) { $part = $remaining; $remaining = '' }
                else {
                    $cut = $remaining.LastIndexOf(' ', [Math]::Min($maxChars - 1, $remaining.Length - 1))
                    if ($cut -gt 0) {
                        $part = $remaining.Substring(0, $cut).TrimEnd()
                        $remaining = $remaining.Substring($cut + 1).TrimStart()
                    } else {
                        $part = $remaining.Substring(0, $maxChars)
                        $remaining = $remaining.Substring($maxChars)
                    }
                    $continuation = $true
                }
                $graphics.DrawString(($prefix + $part), $codeFont, $codeBrush, $x, $y, [System.Drawing.StringFormat]::GenericTypographic)
                $y += 9.0
            }
        }

        # Word source uses the exact source excerpt as separate monospaced paragraphs.
        $pageXml += New-LabelParagraph $sectionTitle 'section'
        $pageXml += New-LabelParagraph $note 'note'
        foreach ($sourceLine in $sourceLines) { $pageXml += New-CodeParagraph $sourceLine }
    }
    $graphics.DrawString("Page $($i + 1) of 12", $smallFont, $mutedBrush, [single]($a4Width - 82), [single]($a4Height - 30))
    if ($y -gt ($a4Height - 47)) { throw "Page $($i + 1) exceeds the safe print area: y=$y pt" }
    $pngPath = Join-Path $qaDir ('page-{0:D2}.png' -f ($i + 1))
    $bitmap.Save($pngPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $pagesPng += $pngPath
    $graphics.Dispose()
    $bitmap.Dispose()

    if ($i -eq 0) { $pageTitle = 'College Darpan Code Appendix' }
    else { $pageTitle = $page.Title }
    $breakStyle = if ($i -gt 0) { 'pagebreak' } else { '' }
    $pageXml += New-LabelParagraph $pageTitle $breakStyle
    if ($i -eq 0) {
        $pageXml += New-LabelParagraph 'Selected implementation excerpts from the existing project. Each excerpt is labeled; omitted source sections are not represented as complete code.' 'note'
    }
}

# Build a minimal, standards-compliant DOCX package without touching source files.
$docParagraphs = [System.Text.StringBuilder]::new()
$pageCursor = 0
for ($i = 0; $i -lt $pages.Count; $i++) {
    if ($i -gt 0) { [void]$docParagraphs.Append((New-LabelParagraph $pages[$i].Title 'pagebreak')) }
    elseif ($i -eq 0) {
        [void]$docParagraphs.Append((New-LabelParagraph 'College Darpan Code Appendix' ''))
        [void]$docParagraphs.Append((New-LabelParagraph 'Selected implementation excerpts from the existing project. Each excerpt is labeled; omitted source sections are not represented as complete code.' 'note'))
    }
    foreach ($section in $pages[$i].Sections) {
        $sectionTitle = "$($section.File) (lines $($section.Start)-$($section.End))"
        [void]$docParagraphs.Append((New-LabelParagraph $sectionTitle 'section'))
        [void]$docParagraphs.Append((New-LabelParagraph $section.Note 'note'))
        foreach ($sourceLine in (Get-SectionLines $section)) { [void]$docParagraphs.Append((New-CodeParagraph $sourceLine)) }
    }
}

$documentXml = @"
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>$($docParagraphs.ToString())<w:sectPr><w:footerReference w:type="default" r:id="rId1"/><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="720" w:right="750" w:bottom="828" w:left="750" w:header="300" w:footer="360" w:gutter="0"/><w:cols w:space="720"/></w:sectPr></w:body></w:document>
"@
$stylesXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="17"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>
'@
$footerXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:pPr><w:jc w:val="right"/><w:spacing w:before="0" w:after="0"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="64748B"/><w:sz w:val="14"/></w:rPr><w:t>Page </w:t></w:r><w:fldSimple w:instr="PAGE"><w:r><w:t>1</w:t></w:r></w:fldSimple><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="64748B"/><w:sz w:val="14"/></w:rPr><w:t xml:space="preserve"> of </w:t></w:r><w:fldSimple w:instr="NUMPAGES"><w:r><w:t>12</w:t></w:r></w:fldSimple></w:p></w:ftr>
'@
$relsXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>
'@
$rootRelsXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>
'@
$contentTypesXml = @'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>
'@

Add-Type -AssemblyName System.IO.Compression
$docxPath = Join-Path $outDir 'College_Darpan_Code_Appendix.docx'
if (Test-Path $docxPath) { Remove-Item -LiteralPath $docxPath -Force }
$fileStream = [System.IO.File]::Open($docxPath, [System.IO.FileMode]::CreateNew)
$archive = [System.IO.Compression.ZipArchive]::new($fileStream, [System.IO.Compression.ZipArchiveMode]::Create, $false)
foreach ($entry in @(
    @{ Name='[Content_Types].xml'; Text=$contentTypesXml },
    @{ Name='_rels/.rels'; Text=$rootRelsXml },
    @{ Name='word/document.xml'; Text=$documentXml },
    @{ Name='word/styles.xml'; Text=$stylesXml },
    @{ Name='word/footer1.xml'; Text=$footerXml },
    @{ Name='word/_rels/document.xml.rels'; Text=$relsXml }
)) {
    $zipEntry = $archive.CreateEntry($entry.Name)
    $writer = [System.IO.StreamWriter]::new($zipEntry.Open(), [System.Text.UTF8Encoding]::new($false))
    $writer.Write($entry.Text)
    $writer.Dispose()
}
$archive.Dispose()
$fileStream.Dispose()

# Convert QA page images to a 12-page A4 image-backed PDF with exact page boxes.
$jpegEncoder = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg' | Select-Object -First 1
$encoderParams = [System.Drawing.Imaging.EncoderParameters]::new(1)
$encoderParams.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new([System.Drawing.Imaging.Encoder]::Quality, [long]94)
$jpegPages = @()
foreach ($pngPath in $pagesPng) {
    $img = [System.Drawing.Image]::FromFile($pngPath)
    $memory = [System.IO.MemoryStream]::new()
    $img.Save($memory, $jpegEncoder, $encoderParams)
    $jpegPages += ,$memory.ToArray()
    $memory.Dispose()
    $img.Dispose()
}

function Bytes-Ascii([string]$s) { return [System.Text.Encoding]::ASCII.GetBytes($s) }
function Write-Bytes($stream, [byte[]]$bytes) { $stream.Write($bytes, 0, $bytes.Length) }
$objects = [System.Collections.Generic.List[byte[]]]::new()
$objects.Add((Bytes-Ascii '<< /Type /Catalog /Pages 2 0 R >>'))
$kids = for ($i=0; $i -lt 12; $i++) { "$(3 + 3*$i) 0 R" }
$objects.Add((Bytes-Ascii "<< /Type /Pages /Kids [ $($kids -join ' ') ] /Count 12 >>"))
for ($i=0; $i -lt 12; $i++) {
    $pageObj = 3 + 3*$i
    $contentObj = $pageObj + 1
    $imageObj = $pageObj + 2
    $objects.Add((Bytes-Ascii "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /XObject << /Im1 $imageObj 0 R >> >> /Contents $contentObj 0 R >>"))
    $content = Bytes-Ascii "q 595.28 0 0 841.89 0 0 cm /Im1 Do Q"
    $contentStream = [System.IO.MemoryStream]::new()
    Write-Bytes $contentStream (Bytes-Ascii "<< /Length $($content.Length) >>`nstream`n")
    Write-Bytes $contentStream $content
    Write-Bytes $contentStream (Bytes-Ascii "`nendstream")
    $objects.Add($contentStream.ToArray())
    $contentStream.Dispose()
    $image = $jpegPages[$i]
    $imageStream = [System.IO.MemoryStream]::new()
    Write-Bytes $imageStream (Bytes-Ascii "<< /Type /XObject /Subtype /Image /Width 2480 /Height 3508 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length $($image.Length) >>`nstream`n")
    Write-Bytes $imageStream $image
    Write-Bytes $imageStream (Bytes-Ascii "`nendstream")
    $objects.Add($imageStream.ToArray())
    $imageStream.Dispose()
}
$pdfStream = [System.IO.MemoryStream]::new()
Write-Bytes $pdfStream (Bytes-Ascii "%PDF-1.4`n%PDF appendix`n")
$offsets = [System.Collections.Generic.List[long]]::new()
for ($i=0; $i -lt $objects.Count; $i++) {
    $offsets.Add($pdfStream.Position)
    Write-Bytes $pdfStream (Bytes-Ascii "$($i+1) 0 obj`n")
    Write-Bytes $pdfStream $objects[$i]
    Write-Bytes $pdfStream (Bytes-Ascii "`nendobj`n")
}
$xrefOffset = $pdfStream.Position
Write-Bytes $pdfStream (Bytes-Ascii "xref`n0 $($objects.Count+1)`n0000000000 65535 f `n")
foreach ($offset in $offsets) { Write-Bytes $pdfStream (Bytes-Ascii ('{0:D10} 00000 n ' -f $offset) + (Bytes-Ascii "`n")) }
Write-Bytes $pdfStream (Bytes-Ascii "trailer`n<< /Size $($objects.Count+1) /Root 1 0 R >>`nstartxref`n$xrefOffset`n%%EOF`n")
$pdfPath = Join-Path $outDir 'College_Darpan_Code_Appendix.pdf'
[System.IO.File]::WriteAllBytes($pdfPath, $pdfStream.ToArray())
$pdfStream.Dispose()

$codeFont.Dispose(); $smallFont.Dispose(); $sectionFont.Dispose(); $titleFont.Dispose(); $noteFont.Dispose()
$darkBrush.Dispose(); $codeBrush.Dispose(); $mutedBrush.Dispose(); $accentBrush.Dispose(); $fontCollection.Dispose()

[pscustomobject]@{ DOCX=$docxPath; PDF=$pdfPath; Pages=$pages.Count; QA=$qaDir; DocxBytes=(Get-Item $docxPath).Length; PdfBytes=(Get-Item $pdfPath).Length }
