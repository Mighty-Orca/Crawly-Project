from app.crawler.base_crawler import BaseCrawler


class DetikCrawler(BaseCrawler):
    """
    Crawler untuk Detik.com.
    Alur: ambil list URL dari halaman search → buka tiap artikel → ekstrak data.
    """

    PORTAL_NAME = 'Detik.com'
    SEARCH_URL  = 'https://www.detik.com/search/searchall?query={keyword}&page={page}'

    # ------------------------------------------------------------------
    # crawl() — entry point, dipanggil dari routes.py
    # ------------------------------------------------------------------
    def crawl(self, max_page=3):
        """Crawl halaman search Detik, ambil artikel dari tiap halaman."""
        for page in range(1, max_page + 1):
            url = self.SEARCH_URL.format(
                keyword=self.keyword.replace(' ', '+'),
                page=page
            )
            print(f"[Detik] Fetching halaman {page}: {url}")

            soup = self.fetch(url)
            if not soup:
                break

            # Ambil semua card artikel di halaman ini
            artikel_urls = self._get_article_urls(soup)
            if not artikel_urls:
                print(f"[Detik] Tidak ada artikel di halaman {page}, berhenti.")
                break

            # Buka tiap artikel dan ekstrak datanya
            for artikel_url in artikel_urls:
                artikel = self._parse_article(artikel_url)
                if artikel:
                    self.results.append(artikel)

        return self.results

    # ------------------------------------------------------------------
    # _get_article_urls() — ambil semua URL artikel dari halaman search
    # ------------------------------------------------------------------
    def _get_article_urls(self, soup):
        urls = []
        SKIP_SUBDOMAIN = ['wolipop', 'sport', '20', 'oto', 'inet', 'food']
        
        cards = soup.find_all('article', class_='list-content__item')
        for card in cards:
            a_tag = card.select_one('h3.media__title a.media__link')
            if a_tag and a_tag.get('href'):
                href = a_tag['href']
                # Skip subdomain non-berita
                subdomain = href.split('//')[1].split('.')[0]
                if subdomain in SKIP_SUBDOMAIN:
                    continue
                urls.append(href)
        return urls
    # ------------------------------------------------------------------
    # _parse_article() — buka satu artikel dan ekstrak semua elemennya
    # ------------------------------------------------------------------
    def _parse_article(self, url):
        soup = self.fetch(url)
        if not soup:
            return None

        # Judul
        judul_tag = soup.find('h1', class_='detail__title')
        judul = judul_tag.get_text(strip=True) if judul_tag else '-'

        # Tanggal
        tanggal_tag = soup.find('div', class_='detail__date')
        tanggal = tanggal_tag.get_text(strip=True) if tanggal_tag else '-'

        # Jurnalis
        author_tag = soup.find('div', class_='detail__author')
        jurnalis = author_tag.get_text(strip=True) if author_tag else '-'

        # Isi — gabungkan semua <p> dalam div.detail__body-text
        isi = '-'
        body = soup.find('div', class_='detail__body-text')
        if body:
            paragraphs = body.find_all('p')
            isi = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        return self.to_dict(judul, tanggal, isi, jurnalis, url, self.PORTAL_NAME)