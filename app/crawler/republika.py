from app.crawler.base_crawler import BaseCrawler


class RepublikaCrawler(BaseCrawler):

    PORTAL_NAME = 'Republika.co.id'
    SEARCH_URL  = 'https://republika.co.id/search/v3/?q={keyword}&page={page}'

    def crawl(self, max_page=3):
        for page in range(1, max_page + 1):
            url = self.SEARCH_URL.format(
                keyword=self.keyword.replace(' ', '+'),
                page=page
            )
            print(f"[Republika] Fetching halaman {page}: {url}")

            soup = self.fetch(url)
            if not soup:
                break

            artikel_urls = self._get_article_urls(soup)
            if not artikel_urls:
                print(f"[Republika] Tidak ada artikel di halaman {page}, berhenti.")
                break

            for artikel_url in artikel_urls:
                artikel = self._parse_article(artikel_url)
                if artikel:
                    self.results.append(artikel)

        return self.results

    def _get_article_urls(self, soup):
        urls = []
        # Container = div.news-item
        cards = soup.find_all('div', class_='news-item')
        for card in cards:
            # URL ada di div.news-title > a
            title_div = card.find('div', class_='news-title')
            if title_div:
                a_tag = title_div.find('a')
                if a_tag and a_tag.get('href'):
                    urls.append(a_tag['href'])
        return urls

    def _parse_article(self, url):
        soup = self.fetch(url)
        if not soup:
            return None

        # Judul — h1 dalam div.max-card__title
        judul = '-'
        title_div = soup.find('div', class_='max-card__title')
        if title_div:
            h1 = title_div.find('h1')
            judul = h1.get_text(strip=True) if h1 else '-'

        # Tanggal — div.date.date-item__headline
        tanggal_tag = soup.find('div', class_='date-item__headline')
        tanggal = tanggal_tag.get_text(strip=True) if tanggal_tag else '-'

        # Jurnalis — ada di div.max-card__title sebagai teks "Rep: Nama/ Red: ..."
        jurnalis = '-'
        if title_div:
            # Ambil semua teks, cari yang mengandung "Rep:"
            teks = title_div.get_text(separator=' ', strip=True)
            if 'Rep:' in teks:
                # Ambil bagian setelah "Rep:" sampai "/"
                try:
                    jurnalis = teks.split('Rep:')[1].split('/')[0].strip()
                except:
                    jurnalis = '-'

        # Isi — semua <p> dalam tag <article>
        isi = '-'
        article_tag = soup.find('article')
        if article_tag:
            paragraphs = []
            for p in article_tag.find_all('p'):
                text = p.get_text(strip=True)
                # Skip paragraf kosong atau spasi saja
                if text and text != '\xa0':
                    paragraphs.append(text)
            isi = ' '.join(paragraphs)

        return self.to_dict(judul, tanggal, isi, jurnalis, url, self.PORTAL_NAME)