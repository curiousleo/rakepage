Rakepage
========

Rakepage is a tiny Rakefile that builds a static website from Markdown pages
and static assets.

Be warned that this is one of those Works For Me (TM) projects -- it's my first
contact with Ruby/Rake and I wrote it both to learn about the language(s) and
because I thought it might make my life a bit easier. I use it to build a
small, static website, and find it very useful.

Usage
-----

This could be the directory structure of a small Rakepage project:

    |- Rakefile
    |- site.yaml
    |- layouts
        |- _default.liquid
        |- _footer.liquid
        |- _header.liquid
        |- ...
    |- media
        |- css
            |- ...
        |- js
            |- ...
    |- output
    |- pages
        |- about.md
        |- contact.md
        |- index.md
        |- ...

Create the directory structure, then copy `Rakefile` and `site.yaml` into the
project's root. Then create your pages, edit the configuration file, and when
you're done...

Run

    rake

(or `rake gen`) to convert all the Markdown pages into HTML, embed them in the
Liquid layout and copy them and the static assets to `output`. Done!

While you are tweaking your site,

    rake auto

is your friend: It simply triggers `rake` whenever a file changes on the
disk -- normally the site is regenerated before you can press Alt-Tab and F5.

Configuration
-------------

See `site.yaml` for all the configuration options.

-- curiousleo
