func generateCSV() {
	log.Printf("Generating %s from %s...\n", CSVFilename, HTMLFilename)

	f, err := os.Open(HTMLFilename)
	if err != nil {
		log.Printf("ERROR: %s not found. Cannot generate CSV.\n", HTMLFilename)
		return
	}
	defer f.Close()

	doc, err := goquery.NewDocumentFromReader(f)
	if err != nil {
		log.Printf("ERROR: Failed to parse HTML: %v\n", err)
		return
	}

	tableBody := doc.Find("table.waffle tbody")
	if tableBody.Length() == 0 {
		log.Println("ERROR: Could not find the table body in HTML. Cannot generate CSV.")
		return
	}

	rows := tableBody.Find("tr")
	var data [][]string
	starringSection := true
	existingArtists := make(map[string]bool)

	rows.Each(func(i int, row *goquery.Selection) {
		if i < 3 {
			return
		}

		cells := row.Find("td")
		if cells.Length() < 4 {
			return
		}

		artistNameRaw := cells.Eq(0).Text()
		artistNameRaw = strings.TrimSpace(artistNameRaw)

		artistURL, _ := cells.Eq(0).Find("a").Attr("href")

		if artistNameRaw == "" || artistURL == "" {
			return
		}

		if strings.Contains(artistNameRaw, "AI Models") {
			starringSection = false
		}

		artistNameClean := cleanArtistName(artistNameRaw)
		if ExcludeNames[artistNameClean] || strings.Contains(artistNameRaw, "🚩") {
			return
		}

		lowerName := strings.ToLower(artistNameClean)
		if strings.Contains(lowerName, "bpm") && strings.Contains(lowerName, "key") {
			return
		}

		credit := strings.TrimSpace(cells.Eq(1).Text())
		linksWork := strings.TrimSpace(cells.Eq(3).Text())
		updated := strings.TrimSpace(cells.Eq(2).Text())
		best := forceStarFlag(starringSection)

		data = append(data, []string{
			artistNameClean,
			artistURL,
			credit,
			linksWork,
			updated,
			best,
		})
		existingArtists[artistNameClean] = true
	})

	for _, manualRow := range ManualCSVRows {
		if len(manualRow) >= 6 {
			artistName := manualRow[0]
			if !existingArtists[artistName] {
				lowerName := strings.ToLower(artistName)
				if strings.Contains(lowerName, "bpm") && strings.Contains(lowerName, "key") {
					continue
				}
				data = append(data, manualRow)
				existingArtists[artistName] = true
			}
		}
	}

	sort.Slice(data, func(i, j int) bool {
		bestI := data[i][5]
		bestJ := data[j][5]
		nameI := data[i][0]
		nameJ := data[j][0]

		if bestI != bestJ {
			return bestI > bestJ
		}
		return strings.ToLower(nameI) < strings.ToLower(nameJ)
	})

	csvFile, err := os.Create(CSVFilename)
	if err != nil {
		log.Printf("ERROR: Failed to create CSV file %s: %v\n", CSVFilename, err)
		return
	}
	defer csvFile.Close()

	header := []string{"Artist Name", "URL", "Credit", "Links Work", "Updated", "Best"}
	if err := writeCSVRow(csvFile, header); err != nil {
		log.Printf("ERROR: Failed to write CSV header: %v\n", err)
		return
	}

	for _, record := range data {
		if err := writeCSVRow(csvFile, record); err != nil {
			log.Printf("ERROR: Failed to write CSV row: %v\n", err)
			return
		}
	}

	log.Printf("SUCCESS: Generated %s with %d rows.\n", CSVFilename, len(data))
}
