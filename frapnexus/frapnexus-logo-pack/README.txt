FrapNexus — logo asset pack
===========================
Mark: "Geometric nexus" — three rotating triangles converging on a hub (the nexus).
Centre is a white halo + navy dot ("eye"), so it reads on light and dark backgrounds.

Palette
  Blue #2563EB   Indigo #4338CA   Teal #0FB5BA   Sky #93C5FD   Navy #16243C
Wordmark: Montserrat SemiBold (Frap = navy, Nexus = blue on light / sky on dark).

Folders
  svg/   editable vector masters (scale to any size)
  png/   transparent / tile PNGs
  jpg/   flattened JPGs (white bg) for places that don't allow PNG
  favicon.ico   multi-size 16/32/48

Which file where
  App icon / marketplace tile .... png/icon-512.png   (light tile, primary)
  Site header (light bg) ......... svg/frapnexus-lockup.svg  /  png/lockup-648.png
  Site header (dark bg) .......... svg/frapnexus-lockup-dark.svg
  Favicon ........................ favicon.ico + png/favicon-32.png
  Apple touch / mobile home ...... png/apple-touch-icon-180.png (also 152, 167)
  PWA / Android .................. png/icon-192.png, png/icon-512.png
  Big logo (transparent) ......... png/mark-1024.png   (JPG: jpg/mark-1024.jpg on white)
  Banner — dark .................. png/banner-1280x640.png  (jpg/...)
  Banner — light ................. png/banner-light-1280x640.png
  Banner — wide header ........... png/banner-1600x400.png
  Single-colour stamp ............ svg/frapnexus-mark-mono-navy.svg / -white.svg
  Dark-surface tile (alt) ........ png/icon-navy-512.png

Frappe hooks.py (after copying icon-512.png into frapnexus/public/images/)
  app_logo_url = "/assets/frapnexus/images/icon-512.png"

HTML <head>
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180.png">

Open preview.html to see everything.
