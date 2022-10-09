# Supported Font Formats
## Italic
The SVG `font-style="italic"` for italic, should be represented as `*Italic*`
## Bold
The SVG `font-weight="bold"` for bold, should be represented as `**Bold**`
## Underline
The SVG `text-decoration="underline"` for underline, should be represented `_Underline_`
## Line-through
The SVG `text-decoration="line-through"`  for strike through, should be represented as `~~strike through~~`
## Inline Code
The `code` (monospace font on grey background), should be represented as ``inline code``
## Links
The SVG representation for a link is:
```
<a xlink:href= "http://example.com/link/" xlink:title="The link leads to an example page that is of little interest">
     <text x="10" y="25" >An example link.</text>
</a>
```
