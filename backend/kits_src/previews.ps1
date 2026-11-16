# Takes a picture of each kit's main file (Excel sheet, PowerPoint slide or Word first page) for the website.
# Called by previews.py with a JSON spec. Needs Microsoft Office installed.
param([string]$SpecPath, [string]$OutDir)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$spec = Get-Content $SpecPath -Raw | ConvertFrom-Json
$order = @("Dashboard", "Weekly report", "Month view", "Monthly P&L", "Variance", "12-month forecast", "Break-even", "Ratios", "Startup budget", "MIS report", "Projections", "Invoice",
           "Comparison", "Market size", "Keywords", "30-day calendar", "Formula demos", "Cleaner", "Pivot-style report", "Fees", "Summary", "Sales", "Financials", "Clean table", "Monthly summary")

function Save-Clip($path) {
  Start-Sleep -Milliseconds 1100
  $img = [System.Windows.Forms.Clipboard]::GetImage()
  if (-not $img) {
    # Word puts a picture on the clipboard as an enhanced metafile: draw it onto a bitmap
    $do = [System.Windows.Forms.Clipboard]::GetDataObject()
    if ($do -and $do.GetDataPresent([System.Windows.Forms.DataFormats]::EnhancedMetafile)) {
      $mf = $do.GetData([System.Windows.Forms.DataFormats]::EnhancedMetafile)
      $w = [int]($mf.Width * 2); $h = [int]($mf.Height * 2)
      $bmp = New-Object System.Drawing.Bitmap $w, $h
      $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::White); $g.DrawImage($mf, 0, 0, $w, $h); $g.Dispose()
      $img = $bmp
    }
  }
  if ($img) { $img.Save($path, [System.Drawing.Imaging.ImageFormat]::Png); $img.Dispose(); return $true }
  return $false
}

$xl = $null; $wd = $null; $pp = $null
foreach ($item in $spec) {
  $png = Join-Path $OutDir ($item.slug + ".png")
  try {
    if ($item.kind -eq "xlsx") {
      if (-not $xl) { $xl = New-Object -ComObject Excel.Application; $xl.Visible = $true; $xl.DisplayAlerts = $false }
      $wb = $xl.Workbooks.Open($item.file, 0, $true); $xl.CalculateFull()
      $name = $null
      foreach ($n in $order) { foreach ($w in $wb.Worksheets) { if ($w.Name -eq $n) { $name = $n; break } }; if ($name) { break } }
      if (-not $name) { $name = $wb.Worksheets.Item([Math]::Min(2, $wb.Worksheets.Count)).Name }
      $ws = $wb.Worksheets.Item($name); $ws.Activate()
      $nCharts = $ws.ChartObjects().Count
      if ($nCharts -gt 0) {
        # include every chart in the picture (charts sit below the data rows), but leave out the chart-data block on the right
        $bottom = 20; $right = 8
        foreach ($co in $ws.ChartObjects()) { $br = $co.BottomRightCell; $bottom = [Math]::Max($bottom, $br.Row + 1); $right = [Math]::Max($right, $br.Column) }
        $right = $right + 1
        $rng = $ws.Range($ws.Cells(1, 1), $ws.Cells([Math]::Min($bottom, 70), $right)).Address($false, $false)
      } elseif ($name -eq "Summary") { $rng = "A1:R36" }
      else {
        $ur = $ws.UsedRange; $rows = [Math]::Min($ur.Rows.Count + $ur.Row - 1, 34); $cols = [Math]::Min($ur.Columns.Count + $ur.Column - 1, 15)
        $rng = $ws.Range($ws.Cells(1, 1), $ws.Cells([Math]::Max($rows, 8), [Math]::Max($cols, 6))).Address($false, $false)
      }
      $ok = $false
      for ($try = 1; $try -le 4 -and -not $ok; $try++) { $ws.Range($rng).CopyPicture(1, 2); $ok = Save-Clip $png }
      if (-not $ok) { "NOIMG $($item.slug)" }
      $wb.Close($false)
    } elseif ($item.kind -eq "pptx") {
      if (-not $pp) { $pp = New-Object -ComObject PowerPoint.Application }
      $pr = $pp.Presentations.Open($item.file, 1, 0, 0)
      $pr.Slides.Item([int]$item.slide).Export($png, "PNG", 1280, 720); $pr.Close()
    } elseif ($item.kind -eq "docx") {
      if (-not $wd) { $wd = New-Object -ComObject Word.Application; $wd.Visible = $true; $wd.DisplayAlerts = 0 }
      $doc = $wd.Documents.Open($item.file, $false, $true)
      $end = $doc.GoTo(1, 1, 2).Start - 1
      if ($end -lt 100) { $end = $doc.Content.End }
      $ok = $false
      for ($try = 1; $try -le 4 -and -not $ok; $try++) { $doc.Range(0, $end).CopyAsPicture(); $ok = Save-Clip $png }
      if (-not $ok) { "NOIMG $($item.slug)" }
      $doc.Close($false)
    }
  } catch { "FAIL $($item.slug): $_" }
}
if ($xl) { $xl.Quit() }
if ($wd) { $wd.Quit() }
if ($pp) { $pp.Quit() }
"done"
