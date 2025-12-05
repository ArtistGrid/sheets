package main

import (
	"archive/zip"
	"bytes"
	"crypto/sha256"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"
	"sort"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

const (
	SheetURL = "https://docs.google.com/spreadsheets/d/1Z8aANbxXbnUGoZPRvJfWL3gz6jrzPPrwVt3d0c1iJ_4"
	ZipURL   = SheetURL + "/export?format=zip"
	XlsxURL  = SheetURL + "/export?format=xlsx"

	ZipFilename  = "Trackerhub.zip"
	HTMLFilename = "Artists.html"
	CSVFilename  = "artists.csv"
	XlsxFilename = "artists.xlsx"

	UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
	BaseURL   = "https://sheets.artistgrid.cx"

	UpdateIntervalSeconds = 600
	InfoPath              = "info/status.json"

	DEV_MODE = false
)

var ExcludeNames = map[string]bool{
	"🎹Worst Comps & Edits":  true,
	"🎹 Yedits":              true,
	"🎹 Comps & Edits":       true,
	"Comps & Edits":         true,
	"Worst Comps & Edits":   true,
	"Yedits":                true,
	"K4$H K4$$!N0":          true,
	"K4HKn0":                true,
	"AI Models":             true,
	"🎹 BPM & Key Tracker":   true,
	"🎹Comps & Edits":        true,
	"🎹 Worst Comps & Edits": true,
	"Allegations":           true,
	"Rap Disses Timeline":   true,
	"Underground Artists":   true,
	"bpmkeytracker":         true,
}

var ManualCSVRows = [][]string{
	{"Kanye West", "https://docs.google.com/spreadsheets/d/1VfpFhHpcLK6G_4sLKykLHV0PdlQar1Fc6sk5TLubMRg/", "p4, @kiwieater, Maker, Bobby, SamV1sion, @comptonrapper, Rose, Dr Wolf, Oreo Eater, Arco, @Free The Robots, @Alek, @Commandtechno, Snoop Dogg, Awesomefied, @rocky, @flab, Shadow, Reuben🇮🇪, @razacosmica, @Marcemaire, Solidus Jack, Marin, garfiiieeelld", "Yes", "Yes", "Yes"},
	{"BI$H", "https://docs.google.com/spreadsheets/d/1d_tTCAIgNmSYvCqx2WuoSfsHcfsRX_mAsvBhI6CPaVM/", "fish (?, dont take my word on this im not sure)", "Yes", "Yes", "Yes"},
	{"mzyxx", "https://docs.google.com/spreadsheets/d/1fbUISzmf3BqhJKwQKl4gegjadO8X6Db77B_TJw1YtsA/", "xyan", "Yes", "Yes", "Yes"},
	{"Unc and Phew", "https://docs.google.com/spreadsheets/d/1-JdaCDJOSA6NTmClTnnmEMBGTqNgaw-RZiQ7ulABpO8/", "xyan, michael", "Yes", "Yes", "Yes"},
	{"Tyler, the Creator", "https://docs.google.com/spreadsheets/d/10jvvqsnTrPbPqtfkJTn24-xrhfAssFQxuDwWY9CpZow/", "?", "Yes", "Yes", "Yes"},
	{"Frank Ocean", "https://docs.google.com/spreadsheets/d/1k-H1rWZo37MiNWtzMlb-fstUv_COQx8lwB5PVky21XA/", "?", "Yes", "Yes", "Yes"},
}

var (
	lastHTMLHash string
	lastCSVData  ArtistData
	emojiRegex   = regexp.MustCompile(`[\p{So}\p{Sk}\x{FE0F}\x{FE0E}\x{200D}⭐🤖🎭︎]+`)
)

type ArtistData map[string]map[string]string

type FileInfo struct {
	Hash string `json:"hash"`
}

type StatusInfo struct {
	LastUpdated string              `json:"last_updated"`
	Files       map[string]FileInfo `json:"files"`
}

type DiscordMessage struct {
	Content string `json:"content"`
}

func cleanArtistName(text string) string {
	cleaned := emojiRegex.ReplaceAllString(text, "")
	cleaned = strings.TrimSpace(cleaned)
	cleaned = strings.TrimPrefix(cleaned, " ")
	return cleaned
}

func forceStarFlag(starred bool) string {
	if starred {
		return "Yes"
	}
	return "No"
}

func hashFile(filename string) (string, error) {
	f, err := os.Open(filename)
	if err != nil {
		return "file_not_found", err
	}
	defer f.Close()

	hasher := sha256.New()
	if _, err := io.Copy(hasher, f); err != nil {
		return "", err
	}

	return hex.EncodeToString(hasher.Sum(nil)), nil
}

func downloadFile(url, filename string, timeout time.Duration) bool {
	log.Printf("Downloading %s...\n", filename)

	client := &http.Client{Timeout: timeout}
	resp, err := client.Get(url)
	if err != nil {
		log.Printf("ERROR: Failed to download %s: %v\n", filename, err)
		return false
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("ERROR: Failed to download %s: status %d\n", filename, resp.StatusCode)
		return false
	}

	out, err := os.Create(filename)
	if err != nil {
		log.Printf("ERROR: Failed to create file %s: %v\n", filename, err)
		return false
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		log.Printf("ERROR: Failed to write file %s: %v\n", filename, err)
		return false
	}

	log.Printf("SUCCESS: Saved %s\n", filename)
	return true
}

func downloadZipAndExtractHTML() {
	if !downloadFile(ZipURL, ZipFilename, 30*time.Second) {
		return
	}

	log.Printf("Extracting %s from %s...\n", HTMLFilename, ZipFilename)

	r, err := zip.OpenReader(ZipFilename)
	if err != nil {
		log.Printf("ERROR: Failed to open zip file: %v\n", err)
		return
	}
	defer r.Close()

	for _, f := range r.File {
		if f.Name == HTMLFilename {
			rc, err := f.Open()
			if err != nil {
				log.Printf("ERROR: Failed to open file in zip: %v\n", err)
				return
			}
			defer rc.Close()

			content, err := io.ReadAll(rc)
			if err != nil {
				log.Printf("ERROR: Failed to read file from zip: %v\n", err)
				return
			}

			err = os.WriteFile(HTMLFilename, content, 0644)
			if err != nil {
				log.Printf("ERROR: Failed to write extracted file: %v\n", err)
				return
			}

			log.Printf("SUCCESS: Extracted %s\n", HTMLFilename)
			return
		}
	}

	log.Printf("ERROR: %s not found in zip archive\n", HTMLFilename)
}

func downloadXLSX() {
	downloadFile(XlsxURL, XlsxFilename, 30*time.Second)
}

func quoteCSVField(field string) string {
	escaped := strings.ReplaceAll(field, `"`, `""`)
	return `"` + escaped + `"`
}

func writeCSVRow(w io.Writer, fields []string) error {
	quotedFields := make([]string, len(fields))
	for i, field := range fields {
		quotedFields[i] = quoteCSVField(field)
	}
	_, err := w.Write([]byte(strings.Join(quotedFields, ",") + "\n"))
	return err
}

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

func readCSVToDict(filename string) ArtistData {
	data := make(ArtistData)

	f, err := os.Open(filename)
	if err != nil {
		log.Printf("WARNING: CSV file not found: %s\n", filename)
		return data
	}
	defer f.Close()

	reader := csv.NewReader(f)
	records, err := reader.ReadAll()
	if err != nil {
		log.Printf("ERROR: Error reading CSV file %s: %v\n", filename, err)
		return data
	}

	if len(records) == 0 {
		return data
	}

	headers := records[0]
	for _, record := range records[1:] {
		if len(record) < len(headers) {
			continue
		}

		row := make(map[string]string)
		for i, header := range headers {
			row[header] = record[i]
		}

		if artistName, ok := row["Artist Name"]; ok && artistName != "" {
			data[artistName] = row
		}
	}

	return data
}

func detectChanges(oldData, newData ArtistData) []string {
	var changes []string

	oldKeys := make(map[string]bool)
	newKeys := make(map[string]bool)

	for k := range oldData {
		oldKeys[k] = true
	}
	for k := range newData {
		newKeys[k] = true
	}

	var removed []string
	for k := range oldKeys {
		if !newKeys[k] {
			removed = append(removed, k)
		}
	}
	sort.Strings(removed)

	var added []string
	for k := range newKeys {
		if !oldKeys[k] {
			added = append(added, k)
		}
	}
	sort.Strings(added)

	var common []string
	for k := range oldKeys {
		if newKeys[k] {
			common = append(common, k)
		}
	}
	sort.Strings(common)

	for _, artist := range removed {
		changes = append(changes, "REMOVED: **"+artist+"**")
	}

	for _, artist := range added {
		changes = append(changes, "ADDED: **"+artist+"**")
	}

	for _, artist := range common {
		oldRow := oldData[artist]
		newRow := newData[artist]

		if oldRow["URL"] != newRow["URL"] {
			changes = append(changes, "LINK CHANGED: **"+artist+"**")
		}
		if oldRow["Credit"] != newRow["Credit"] {
			changes = append(changes, "CREDIT CHANGED: **"+artist+"**")
		}
		if oldRow["Links Work"] != newRow["Links Work"] {
			changes = append(changes, "LINKS WORK STATUS CHANGED: **"+artist+"**")
		}
		if oldRow["Updated"] != newRow["Updated"] {
			changes = append(changes, "UPDATED DATE CHANGED: **"+artist+"**")
		}
		if oldRow["Best"] != newRow["Best"] {
			changes = append(changes, "BEST FLAG CHANGED: **"+artist+"**")
		}
	}

	return changes
}

func sendDiscordMessage(content string) {
	webhookURL := os.Getenv("DISCORD_WEBHOOK_URL")
	if webhookURL == "" {
		log.Println("WARNING: Discord webhook URL not set. Skipping notification.")
		return
	}

	if len(content) > 2000 {
		content = content[:1990] + "\n... (truncated)"
	}

	message := DiscordMessage{Content: content}
	jsonData, err := json.Marshal(message)
	if err != nil {
		log.Printf("WARNING: Failed to marshal Discord message: %v\n", err)
		return
	}

	resp, err := http.Post(webhookURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Printf("WARNING: Exception sending Discord notification: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		log.Println("SUCCESS: Discord notification sent successfully.")
	} else {
		log.Printf("WARNING: Discord notification failed with status: %d\n", resp.StatusCode)
	}
}

func writeInfo(htmlHash, csvHash, xlsxHash string) {
	os.MkdirAll("info", 0755)
	nowISO := time.Now().UTC().Format(time.RFC3339)

	var info StatusInfo

	data, err := os.ReadFile(InfoPath)
	if err == nil {
		json.Unmarshal(data, &info)
	}

	if info.Files == nil {
		info.Files = make(map[string]FileInfo)
	}

	info.LastUpdated = nowISO
	info.Files[HTMLFilename] = FileInfo{Hash: htmlHash}
	info.Files[CSVFilename] = FileInfo{Hash: csvHash}
	info.Files[XlsxFilename] = FileInfo{Hash: xlsxHash}

	jsonData, err := json.MarshalIndent(info, "", "  ")
	if err != nil {
		log.Printf("WARNING: Failed to marshal status info: %v\n", err)
		return
	}

	os.WriteFile(InfoPath, jsonData, 0644)
}

func runDevTests() {
	log.Println("=== DEVELOPMENT MODE - Running Tests ===")

	log.Println("\nTesting Discord Webhook...")
	testMessage := fmt.Sprintf("**Development Mode Test**\nTimestamp: %s\nWebhook is working correctly!", time.Now().Format(time.RFC3339))
	sendDiscordMessage(testMessage)

	log.Println("\nDevelopment tests completed!")
	log.Println("=========================================\n")
}

func updateLoop() {
	for {
		log.Println("--- Starting update cycle ---")

		downloadZipAndExtractHTML()
		downloadXLSX()
		generateCSV()

		files := []string{HTMLFilename, CSVFilename, XlsxFilename}
		allExist := true
		for _, f := range files {
			if _, err := os.Stat(f); os.IsNotExist(err) {
				allExist = false
				break
			}
		}

		if !allExist {
			log.Println("WARNING: One or more files are missing after download/parse. Skipping this cycle.")
			time.Sleep(UpdateIntervalSeconds * time.Second)
			continue
		}

		htmlHash, _ := hashFile(HTMLFilename)
		csvHash, _ := hashFile(CSVFilename)
		xlsxHash, _ := hashFile(XlsxFilename)
		currentCSVData := readCSVToDict(CSVFilename)

		if lastHTMLHash == "" {
			log.Println("INFO: First run: storing initial file hashes.")
		} else if htmlHash != lastHTMLHash {
			log.Println("ALERT: Artists.html has changed! Checking for data differences.")
			changes := detectChanges(lastCSVData, currentCSVData)
			if len(changes) > 0 {
				message := "**Tracker Update Detected:**\n" + strings.Join(changes, "\n")
				sendDiscordMessage(message)
			} else {
				log.Println("INFO: HTML hash changed, but no data differences found.")
			}
		} else {
			log.Println("INFO: Artists.html is unchanged.")
		}

		writeInfo(htmlHash, csvHash, xlsxHash)
		lastHTMLHash = htmlHash
		lastCSVData = currentCSVData

		log.Println("--- Update cycle finished ---")
		log.Printf("Sleeping for %d seconds...\n", UpdateIntervalSeconds)
		time.Sleep(UpdateIntervalSeconds * time.Second)
	}
}

func getStatusData() (*StatusInfo, error) {
	data, err := os.ReadFile(InfoPath)
	if err != nil {
		return nil, err
	}

	var status StatusInfo
	err = json.Unmarshal(data, &status)
	if err != nil {
		return nil, err
	}

	return &status, nil
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	if DEV_MODE {
		runDevTests()
	}

	log.Println("Starting background update goroutine...")
	go updateLoop()

	app := fiber.New()
	app.Use(cors.New())

	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendFile("templates/index.html")
	})

	app.Get("/robots.txt", func(c *fiber.Ctx) error {
		return c.SendFile("templates/robots.txt")
	})

	app.Get("/artists.html", func(c *fiber.Ctx) error {
		return c.SendFile(HTMLFilename)
	})

	app.Get("/artists.csv", func(c *fiber.Ctx) error {
		return c.SendFile(CSVFilename)
	})

	app.Get("/artists.xlsx", func(c *fiber.Ctx) error {
		return c.SendFile(XlsxFilename)
	})

	app.Static("/_next", "templates/_next")

	app.Get("/info", func(c *fiber.Ctx) error {
		data, err := getStatusData()
		if err != nil {
			return c.Status(404).JSON(fiber.Map{"error": "Info not available"})
		}
		return c.JSON(data)
	})

	app.Get("/info/html", func(c *fiber.Ctx) error {
		data, err := getStatusData()
		if err != nil {
			c.Set("Content-Type", "text/html")
			return c.Status(404).SendString("<p>Status info not available.</p>")
		}

		htmlInfo := data.Files[HTMLFilename]
		csvInfo := data.Files[CSVFilename]
		xlsxInfo := data.Files[XlsxFilename]

		html := fmt.Sprintf(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Info</title>
    <style>body { font-family: sans-serif; } li { margin-bottom: 1em; }</style>
</head>
<body>
    <h1>Latest File Info</h1>
    <p><strong>Last Updated:</strong> %s</p>
    <ul>
        <li><strong>%s</strong><br>
            Hash: %s
        </li>
        <li><strong>%s</strong><br>
            Hash: %s
        </li>
        <li><strong>%s</strong><br>
            Hash: %s
        </li>
    </ul>
</body>
</html>
`, data.LastUpdated,
			HTMLFilename, htmlInfo.Hash,
			CSVFilename, csvInfo.Hash,
			XlsxFilename, xlsxInfo.Hash)

		c.Set("Content-Type", "text/html")
		return c.SendString(html)
	})

	app.Use(func(c *fiber.Ctx) error {
		return c.Status(404).SendFile("templates/404.html")
	})

	log.Println("Starting Fiber server on :5000...")
	log.Fatal(app.Listen(":5000"))
}
