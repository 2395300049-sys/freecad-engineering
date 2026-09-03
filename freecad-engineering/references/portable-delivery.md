# Portable Delivery

The portable package must rebuild from advertised inputs only. Do not rely on absolute project paths, temporary files, extracted BREP caches, or an already-open FreeCAD document.

## Required package

- one documented main Python script;
- every required external source file, such as the accepted STEP;
- optional PowerShell launcher with configurable FreeCAD path;
- concise execution instructions embedded in the Skill or script header;
- deterministic output directory.

## Script requirements

- import only modules expected in the target FreeCAD installation;
- handle missing `__file__` in the FreeCAD Python console;
- avoid Markdown-corrupted identifiers such as `**file**`;
- accept paths containing spaces and non-ASCII characters;
- create valid part and assembly documents with non-null solids;
- write FCStd, STEP, STL, and metrics with current timestamps;
- print the final part and occurrence counts.

## Clean-room test

1. Copy only portable files to a new directory.
2. Delete or ignore prior outputs.
3. Execute through the documented launcher or `FreeCADCmd`.
4. Confirm every expected numbered part exists in FCStd, STEP, and STL.
5. Compare volumes and bounds to the accepted ledger.
6. Count physical assembly children, excluding `App::Part` aggregate shapes.
7. Open the generated assembly in FreeCAD GUI and fit the view.

Report the FreeCAD version, command used, output path, counts, and any remaining external dependency.
