# Broken Links

This is a small Python3 tool for scanning a website and looking for broken links. It tries to deal with anchors as well within the links. It requires requests to be installed.

## Example Usage

Below is a command that will scan all linked pages from that URL that also include that URL. It deals with some Github-Pages idiosyyncracies and then logs all the broken links to a file.

```
python scan.py --url http://swcarpentry.github.io/shell-novice --ghpages --log broken.log
```

## Options

```
  --url URL        URL to start from
  --filter FILTER  Alternative filter to use on URLs on whether to scan them
                   as well
  --log LOG        Log file to output scan
  --all            Log all links, not just the links that fail
  --images         Check images as well as links
  --ghpages        Tidy up output for a GitHub pages site. Deal with the fact
                   that github-pages does not require ignore .html at end of
                   URLs
```
