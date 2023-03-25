PDF Search
-

PDF Search is an algorithm to search for text in pdfs contained in a specified by user folder.

- Store all data in one file for fast search
- Analyze text in pdf
- Analyze text as an image with tesseract
- Load 'all strings' or 'filter by element pattern'
- Search by 'phrase in string' or 'exact match'

Instruction for users with freezed program.
-
1. Extract the contents of the archive to a folder, e.g. to a folder on your desktop
2. Run 'PDF Search.exe'
3. Open the settings and choose how to download and search data ('Menu' -> 'Settings' -> 'Apply')
4. Download the pdf data. ('Menu' -> 'Reload data' -> Point to folder address -> 'Load data').
5. Search for item names. E.g. B_100 (Complete the name -> 'Search').
6. Double-click the selected drawing to open it in the default viewer.


Search for text in pdfs where text cannot be selected
-

To analyze these types of files you can use Tesseract OCR. This type of data collection from the file is much
slower because the pdf is analyzed as an image.

Tesseract ORC installation instructions:
1. Install 'tesseract-ocr-w64-setup-....exe' (remember the location where you install)
2. Copy the language files (e.g., "...\Tesseract-OCR\tessdata\pol.traineddata") to the folder with tesseract.
3. Open 'PDF Search' -> 'Menu' -> 'Settings'
4. In 'Tesseract path', type the location of the file ('...Tesseract-OCR\tesseract.exe')
5. In 'Tesseract language' enter the language in which the file is to be analyzed (eng, pol, ...).
You can find the language files at https://github.com/tesseract-ocr/tessdata