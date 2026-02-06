import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.FileWriter;
import java.net.URI;
import java.util.*;

public class VideoPlaylistScraper {

    static final String START_URL = "https://www.eporner.com/tag/qos/";
    static final String OUTPUT = "playlist.m3u8";

    static final List<String> KEYWORDS = List.of(
            "qos", "hotwife", "cuckold", "bbcslut"
    );

    static final List<String> VIDEO_EXTENSIONS = List.of(
            ".mp4", ".webm", ".mkv", ".avi", ".mov", ".m3u8"
    );

    static final int MAX_PAGES = 50;

    // --------------------------------------------
    static boolean titleMatches(String title) {
        String t = title.toLowerCase();
        return KEYWORDS.stream().anyMatch(t::contains);
    }

    // --------------------------------------------
    static boolean looksLikeVideo(String url) {
        String lower = url.toLowerCase();
        return VIDEO_EXTENSIONS.stream().anyMatch(lower::endsWith);
    }

    // --------------------------------------------
    static Set<String> extractLinks(Document doc, String baseHost) {
        Set<String> links = new HashSet<>();

        for (Element a : doc.select("a[href]")) {
            String abs = a.absUrl("href");
            if (!abs.isEmpty() && URI.create(abs).getHost().equals(baseHost)) {
                links.add(abs);
            }
        }
        return links;
    }

    // --------------------------------------------
    static List<VideoEntry> extractVideos(Document doc) {
        List<VideoEntry> videos = new ArrayList<>();
        String pageTitle = doc.title().isEmpty() ? "Untitled" : doc.title();

        // <video> and <source>
        for (Element video : doc.select("video")) {
            String title = video.hasAttr("title") ? video.attr("title") : pageTitle;

            if (!titleMatches(title)) continue;

            if (video.hasAttr("src")) {
                videos.add(new VideoEntry(title, video.absUrl("src")));
            }

            for (Element source : video.select("source[src]")) {
                videos.add(new VideoEntry(title, source.absUrl("src")));
            }
        }

        // <a href="video.xxx">
        for (Element a : doc.select("a[href]")) {
            String url = a.absUrl("href");
            if (looksLikeVideo(url)) {
                String title = a.text().isBlank() ? pageTitle : a.text();
                if (titleMatches(title)) {
                    videos.add(new VideoEntry(title, url));
                }
            }
        }

        return videos;
    }

    // --------------------------------------------
    static List<VideoEntry> crawlSite() throws Exception {
        Set<String> visited = new HashSet<>();
        Set<String> toVisit = new HashSet<>();
        List<VideoEntry> results = new ArrayList<>();

        URI start = URI.create(START_URL);
        String host = start.getHost();
        toVisit.add(START_URL);

        while (!toVisit.isEmpty() && visited.size() < MAX_PAGES) {
            String url = toVisit.iterator().next();
            toVisit.remove(url);

            if (visited.contains(url)) continue;
            visited.add(url);

            System.out.println("Crawling: " + url);

            Document doc = Jsoup.connect(url)
                    .userAgent("Mozilla/5.0")
                    .timeout(20000)
                    .get();

            results.addAll(extractVideos(doc));
            toVisit.addAll(extractLinks(doc, host));
        }

        // de-duplicate
        return new ArrayList<>(new LinkedHashSet<>(results));
    }

    // --------------------------------------------
    static void writePlaylist(List<VideoEntry> videos) throws Exception {
        try (FileWriter fw = new FileWriter(OUTPUT)) {
            fw.write("#EXTM3U\n");
            for (VideoEntry v : videos) {
                fw.write("#EXTINF:-1," + v.title + "\n");
                fw.write(v.url + "\n");
            }
        }
    }

    // --------------------------------------------
    public static void main(String[] args) throws Exception {
        List<VideoEntry> videos = crawlSite();
        writePlaylist(videos);
        System.out.println("Saved " + videos.size() + " videos to " + OUTPUT);
    }

    // --------------------------------------------
    static class VideoEntry {
        String title;
        String url;

        VideoEntry(String title, String url) {
            this.title = title.trim();
            this.url = url;
        }

        @Override
        public boolean equals(Object o) {
            return o instanceof VideoEntry v && url.equals(v.url);
        }

        @Override
        public int hashCode() {
            return url.hashCode();
        }
    }
}
