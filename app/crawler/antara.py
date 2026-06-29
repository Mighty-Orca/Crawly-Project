from app.crawler.base_crawler import BaseCrawler


class AntaraCrawler(BaseCrawler):

    PORTAL_NAME = 'Antaranews.com'
    SEARCH_URL  = 'https://www.antaranews.com/search?q={keyword}&page={page}'

    def crawl(self, max_page=3):
        for page in range(1, max_page + 1):
            url = self.SEARCH_URL.format(
                keyword=self.keyword.replace(' ', '+'),
                page=page
            )
            print(f"[Antara] Fetching halaman {page}: {url}")

            soup = self.fetch(url)
            if not soup:
                break

            artikel_urls = self._get_article_urls(soup)
            if not artikel_urls:
                print(f"[Antara] Tidak ada artikel di halaman {page}, berhenti.")
                break

            for artikel_url in artikel_urls:
                artikel = self._parse_article(artikel_url)
                if artikel:
                    self.results.append(artikel)

        return self.results

    def _get_article_urls(self, soup):
        urls = []
        # Container = div.card__post
        cards = soup.find_all('div', class_='card__post')
        for card in cards:
            # URL ada di div.card__post__title > h2 > a
            title_div = card.find('div', class_='card__post__title')
            if title_div:
                a_tag = title_div.find('a')
                if a_tag and a_tag.get('href'):
                    urls.append(a_tag['href'])
        return urls

    def _parse_article(self, url):
        soup = self.fetch(url)
        if not soup:
            return None

        # Judul
        judul = '-'
        title_div = soup.find('div', class_='wrap__article-detail-title')
        if title_div:
            h1 = title_div.find('h1')
            judul = h1.get_text(strip=True) if h1 else '-'

        # Tanggal — <span> yang mengandung fa-calendar
        tanggal = '-'
        for li in soup.find_all('li', class_='list-inline-item'):
            if li.find('i', class_='fa-calendar'):
                tanggal = li.get_text(strip=True)
                break

        # Jurnalis — <p class="text-muted"> yang mengandung "Pewarta:"
        jurnalis = '-'
        for p in soup.find_all('p', class_='text-muted'):
            text = p.get_text(strip=True)
            if 'Pewarta:' in text:
                try:
                    jurnalis = text.split('Pewarta:')[1].split('Editor:')[0].strip()
                except:
                    jurnalis = '-'
                break

        # Isi — semua <p> dalam div.wrap__article-detail-content
        isi = '-'
        body = soup.find('div', class_='wrap__article-detail-content')
        if body:
            paragraphs = []
            for p in body.find_all('p'):
                text = p.get_text(strip=True)
                # Skip paragraf copyright dan peringatan crawling
                if text and 'Copyright' not in text and 'Dilarang' not in text:
                    paragraphs.append(text)
            isi = ' '.join(paragraphs)

        return self.to_dict(judul, tanggal, isi, jurnalis, url, self.PORTAL_NAME)