from app.crawler.base_crawler import BaseCrawler


class RRICrawler(BaseCrawler):

    PORTAL_NAME = 'RRI.co.id'
    SEARCH_URL  = 'https://rri.co.id/search?q={keyword}&page={page}'

    def crawl(self, max_page=3):
        for page in range(1, max_page + 1):
            url = self.SEARCH_URL.format(
                keyword=self.keyword.replace(' ', '+'),
                page=page
            )
            print(f"[RRI] Fetching halaman {page}: {url}")

            soup = self.fetch(url)
            if not soup:
                break

            artikel_urls = self._get_article_urls(soup)
            if not artikel_urls:
                print(f"[RRI] Tidak ada artikel di halaman {page}, berhenti.")
                break

            for artikel_url in artikel_urls:
                artikel = self._parse_article(artikel_url)
                if artikel:
                    self.results.append(artikel)

        return self.results

    def _get_article_urls(self, soup):
        urls = []
        # Container = div.news-list-item
        cards = soup.find_all('div', class_='news-list-item')
        for card in cards:
            # URL ada di a.title dalam h4
            a_tag = card.find('a', class_='title')
            if a_tag and a_tag.get('href'):
                urls.append(a_tag['href'])
        return urls

    def _parse_article(self, url):
        soup = self.fetch(url)
        if not soup:
            return None

        # Judul
        judul_tag = soup.find('h2', id='news-title')
        judul = judul_tag.get_text(strip=True) if judul_tag else '-'

        # Tanggal — li.date
        tanggal_tag = soup.find('li', class_='date')
        tanggal = tanggal_tag.get_text(strip=True) if tanggal_tag else '-'

        # Jurnalis — li.author > a
        jurnalis = '-'
        author_li = soup.find('li', class_='author')
        if author_li:
            text = author_li.get_text(strip=True)
            # Format: "Oleh - Noviyanti,"
            jurnalis = text.replace('Oleh -', '').replace(',', '').strip()

        # Isi — semua <p> dalam div konten artikel
        isi = '-'
        # RRI pakai div tanpa class khusus, ambil div yang berisi banyak <p>
        content_div = soup.find('div', class_='news-content')
        if not content_div:
            # Fallback: cari div yang langsung berisi <p> dengan span.s1
            for div in soup.find_all('div'):
                if div.find('span', class_='s1'):
                    content_div = div
                    break

        if content_div:
            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    paragraphs.append(text)
            isi = ' '.join(paragraphs)

        return self.to_dict(judul, tanggal, isi, jurnalis, url, self.PORTAL_NAME)