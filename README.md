# Broken Links

This is a small Python3 tool for scanning a website and looking for broken links. It tries to deal with anchors as well within the links. It requires requests to be installed.

## Example Usage

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
  --ghpages        Deal with the fact that github-pages does not require
                   ignore .html at end of URLs
```
