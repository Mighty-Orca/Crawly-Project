from app.crawler.base_crawler import BaseCrawler


class BeritaSatuCrawler(BaseCrawler):

    PORTAL_NAME = 'BeritaSatu.com'
    SEARCH_URL  = 'https://www.beritasatu.com/search/{keyword}?page={page}'

    def crawl(self, max_page=3):
        for page in range(1, max_page + 1):
            url = self.SEARCH_URL.format(
                keyword=self.keyword.replace(' ', '+'),
                page=page
            )
            print(f"[BeritaSatu] Fetching halaman {page}: {url}")

            soup = self.fetch(url)
            if not soup:
                break

            artikel_urls = self._get_article_urls(soup)
            if not artikel_urls:
                print(f"[BeritaSatu] Tidak ada artikel di halaman {page}, berhenti.")
                break

            for artikel_url in artikel_urls:
                artikel = self._parse_article(artikel_url)
                if artikel:
                    self.results.append(artikel)

        return self.results

    def _get_article_urls(self, soup):
        urls = []
        # Container = div.row.mt-4.position-relative
        # URL ada di a.stretched-link
        cards = soup.find_all('div', class_='position-relative')
        for card in cards:
            a_tag = card.find('a', class_='stretched-link')
            if a_tag and a_tag.get('href'):
                href = a_tag['href']
                if 'beritasatu.com' in href:
                    urls.append(href)
        # Hapus duplikat
        return list(dict.fromkeys(urls))

    def _parse_article(self, url):
        soup = self.fetch(url)
        if not soup:
            return None

        # Judul
        judul_tag = soup.find('h1', class_='fw-bold')
        judul = judul_tag.get_text(strip=True) if judul_tag else '-'

        # Tanggal — <small class="text-muted">
        tanggal = '-'
        for small in soup.find_all('small', class_='text-muted'):
            text = small.get_text(strip=True)
            if 'WIB' in text:
                tanggal = text
                break

        # Jurnalis — div yang mengandung "Penulis:"
        jurnalis = '-'
        for div in soup.find_all('div', class_='my-auto'):
            text = div.get_text(strip=True)
            if 'Penulis:' in text:
                try:
                    jurnalis = text.split('Penulis:')[1].split('|')[0].strip()
                except:
                    jurnalis = '-'
                break

        # Isi — semua <p> dalam div.b1-article
        isi = '-'
        body = soup.find('div', class_='b1-article')
        if body:
            paragraphs = []
            for p in body.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    paragraphs.append(text)
            isi = ' '.join(paragraphs)

        return self.to_dict(judul, tanggal, isi, jurnalis, url, self.PORTAL_NAME)