# App-only release format

Configure an owner/repository in Updates. Publish latest-release assets cytools-app.zip and cytools-app.zip.sha256 (a SHA256 hex string). ZIP contains app/ only, including CyTool.json and release.json. Manifest ID: cy.tools.subtitle. Fixed runtime ABI: py311-fermion0214-core0101-subtitle1. Platform: win32 or any. Maximum uncompressed contents: 256 MiB / 10,000 entries. Archive members must be confined regular files/directories, with no symlinks or traversal.

The source package is distinct: it also includes the native launchers and guide, and excludes data/, runtime/, weights and caches. App-only releases preserve the existing tested environment and cannot add dependencies. Build/test a new environment before changing ABI or redistributing a runtime. The activation lock and active-process checks defer replacement while jobs or another app instance are present. Failed activation restores the original app; the previous version remains selectable.
