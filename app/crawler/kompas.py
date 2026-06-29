from app.crawler.base_crawler import BaseCrawler


class KompasCrawler(BaseCrawler):

    PORTAL_NAME = 'Kompas.com'
    SEARCH_URL = 'https://search.kompas.com/search/?q={keyword}&sort=latest&page={page}'

    def crawl(self, max_page=3):
        for page in range(1, max_page + 1):
            url = self.SEARCH_URL.format(
                keyword=self.keyword.replace(' ', '+'),
                page=page
            )
            print(f"[Kompas] Fetching halaman {page}: {url}")

            soup = self.fetch(url)
            if not soup:
                break

            artikel_urls = self._get_article_urls(soup)
            if not artikel_urls:
                print(f"[Kompas] Tidak ada artikel di halaman {page}, berhenti.")
                break

            for artikel_url in artikel_urls:
                artikel = self._parse_article(artikel_url)
                if artikel:
                    self.results.append(artikel)

        return self.results

    def _get_article_urls(self, soup):
        urls = []
        # Container tiap card = div.articleItem
        # URL ada di a.article-link langsung di dalam div.articleItem
        cards = soup.find_all('div', class_='articleItem')
        for card in cards:
            a_tag = card.find('a', class_='article-link')
            if a_tag and a_tag.get('href'):
                urls.append(a_tag['href'])
        return urls

    def _parse_article(self, url):
        soup = self.fetch(url)
        if not soup:
            return None

        # Judul
        judul_tag = soup.find('h1', class_='read__title')
        judul = judul_tag.get_text(strip=True) if judul_tag else '-'

        # Tanggal
        tanggal_tag = soup.find('div', class_='read__time')
        tanggal = tanggal_tag.get_text(strip=True) if tanggal_tag else '-'

        # Jurnalis
        jurnalis_tag = soup.find('div', class_='credit-title-nameEditor')
        jurnalis = jurnalis_tag.get_text(strip=True) if jurnalis_tag else '-'

        # Isi — semua <p> dalam div.read__content
        isi = '-'
        body = soup.find('div', class_='read__content')
        if body:
            paragraphs = body.find_all('p')
            isi = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        return self.to_dict(judul, tanggal, isi, jurnalis, url, self.PORTAL_NAME)