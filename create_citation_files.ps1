# Script to create CITATION.cff files for all papers without them
$ErrorActionPreference = "Continue"

$papersPath = ".\papers"
$year = 2025

Write-Host "Processing 2025 folder..."
Get-ChildItem -Path "$papersPath\$year" -Directory | ForEach-Object {
    $cffPath = "$($_.FullName)\CITATION.cff"
    
    if (!(Test-Path $cffPath)) {
        $docxFile = Get-ChildItem -Path $_.FullName -Filter "*.docx" | Select-Object -First 1
        if ($docxFile) {
            $titleRu = [System.IO.Path]::GetFileNameWithoutExtension($docxFile.Name)
            $titleRu = $titleRu -replace '^\p{C}+', ''
            
            $content = @"
cff-version: 1.2.0
message: "If you use this work in your research, please cite the following publication."
authors:
  - family-names: "Dupley"
    given-names: "Maxim"
    orcid: "https://orcid.org/0009-0007-7605-539X"
    email: "maksimqwe42@mail.ru"
title: "$titleRu"
version: 1.0
date-released: $year-01-01
url: "https://github.com/QuadDarv1ne/scientific-publications/tree/main/papers/$year"
license: CC-BY-4.0
type: article
keywords:
  - scientific publication
abstract: |
  Scientific publication by Maxim Dupley.
contact:
  - family-names: "Dupley"
    given-names: "Maxim"
    email: "maksimqwe42@mail.ru"
    address: "Moscow, Russia"
"@
            Set-Content -Path $cffPath -Value $content -Encoding UTF8
            Write-Host "Created: $cffPath"
        }
    }
}

Write-Host "Processing 2026 folder..."
$year = 2026
Get-ChildItem -Path "$papersPath\$year" -Directory | ForEach-Object {
    $cffPath = "$($_.FullName)\CITATION.cff"
    
    if (!(Test-Path $cffPath)) {
        $docxFile = Get-ChildItem -Path $_.FullName -Filter "*.docx" | Select-Object -First 1
        $pdfFile = Get-ChildItem -Path $_.FullName -Filter "*.pdf" | Select-Object -First 1
        
        $titleRu = ""
        if ($docxFile) {
            $titleRu = [System.IO.Path]::GetFileNameWithoutExtension($docxFile.Name)
        } elseif ($pdfFile) {
            $titleRu = [System.IO.Path]::GetFileNameWithoutExtension($pdfFile.Name)
        } else {
            $titleRu = $_.Name
        }
        $titleRu = $titleRu -replace '^\p{C}+', ''
        
        $content = @"
cff-version: 1.2.0
message: "If you use this work in your research, please cite the following publication."
authors:
  - family-names: "Dupley"
    given-names: "Maxim"
    orcid: "https://orcid.org/0009-0007-7605-539X"
    email: "maksimqwe42@mail.ru"
title: "$titleRu"
version: 1.0
date-released: $year-01-01
url: "https://github.com/QuadDarv1ne/scientific-publications/tree/main/papers/$year"
license: CC-BY-4.0
type: article
keywords:
  - scientific publication
abstract: |
  Scientific publication by Maxim Dupley.
contact:
  - family-names: "Dupley"
    given-names: "Maxim"
    email: "maksimqwe42@mail.ru"
    address: "Moscow, Russia"
"@
        Set-Content -Path $cffPath -Value $content -Encoding UTF8
        Write-Host "Created: $cffPath"
    }
}

# Also handle Zebra folder
Write-Host "Processing Zebra folder..."
$zebraPath = "$papersPath\2025\Издательство Zebra"
if (Test-Path $zebraPath) {
    Get-ChildItem -Path $zebraPath -Directory | ForEach-Object {
        $cffPath = "$($_.FullName)\CITATION.cff"
        
        if (!(Test-Path $cffPath)) {
            $docxFile = Get-ChildItem -Path $_.FullName -Filter "*.docx" | Select-Object -First 1
            
            $titleRu = ""
            if ($docxFile) {
                $titleRu = [System.IO.Path]::GetFileNameWithoutExtension($docxFile.Name)
            } else {
                $titleRu = $_.Name
            }
            $titleRu = $titleRu -replace '^\p{C}+', ''
            
            $content = @"
cff-version: 1.2.0
message: "If you use this work in your research, please cite the following publication."
authors:
  - family-names: "Dupley"
    given-names: "Maxim"
    orcid: "https://orcid.org/0009-0007-7605-539X"
    email: "maksimqwe42@mail.ru"
title: "$titleRu"
version: 1.0
date-released: 2025-01-01
url: "https://github.com/QuadDarv1ne/scientific-publications/tree/main/papers/2025/Издательство Zebra"
license: CC-BY-4.0
type: article
keywords:
  - scientific publication
abstract: |
  Scientific publication by Maxim Dupley.
contact:
  - family-names: "Dupley"
    given-names: "Maxim"
    email: "maksimqwe42@mail.ru"
    address: "Moscow, Russia"
"@
            Set-Content -Path $cffPath -Value $content -Encoding UTF8
            Write-Host "Created: $cffPath"
        }
    }
}

Write-Host "Done! CITATION.cff files created for all papers."
