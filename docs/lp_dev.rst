.. _lp-dev:

****************************************
Linkage Priority Developer Documentation
****************************************

**Linkage Priority Developer Documentation**

*Version 3.0—Updated October 2020*

John Gallo\ :sup:`1`, Randal Greene\ :sup:`2`\ and Darren
Kavanagh\ :sup:`3`

:sup:`1`\ Conservation Biology Institute

:sup:`2`\ Feaver’s Lane

:sup:`3`\ Torilis, LLC

**Table of Contents**

`1 Introduction <#introduction>`__

`2 Coding Conventions <#coding-conventions>`__

`3 LP Code Organization <#lp-code-organization>`__

`3.1 lp_settings.py <#lp_settings.py>`__

`3.2 lp_main.py <#lp_main.py>`__

`3.3 Summary Diagram of all the modules <#summary-diagram-of-all-the-modules>`__

`3.4 Linkage Mapper.tbx <#linkage-mapper.tbx>`__

`3.5 LpDlgContent.xsl <#lpdlgcontent.xsl>`__

`4 Geoprocessing Summary <#geoprocessing-summary>`__

`5 LP Functions <#lp-functions>`__

`5.1 lp_main.py <#lp_main.py-1>`__

`6 LM Architecture <#lm-architecture>`__

`6.1 Configuration and Settings 10 <#configuration-and-settings>`__

`6.2 Logging <#logging>`__

`6.3 Other Utilities <#other-utilities>`__

`7 Other Notes <#other-notes>`__

`7.1 Source Control Using GitHub <#source-control-using-github>`__

`7.2 Debugging <#debugging>`__

`7.3 Becoming a Linkage Mapper Contributor <#becoming-a-linkage-mapper-contributor>`__

`7.4 Future Enhancements <#future-enhancements>`__

Introduction
============

Linkage Priority (LP) is an ArcGIS geoprocessing script tool, written in
the Python programming language, that is included as part of the Linkage
Mapper (LM) toolbox. Developers should first understand LM and LP
functionality from the user’s perspective. Please review the following
user-oriented introductory material:

-  Linkage Mapper User Guide, including the LM tutorial.

-  Linkage Priority User Guide, including the LP tutorial. Pay
   particular attention to the Geoprocessing Overview for high-level
   introduction to the processing logic that underlies LP.

-  Linkage Mapper web site (https://circuitscape.org/linkagemapper) and
   related publications (https://circuitscape.org/pubs).

Developers should also be familiar with the ArcGIS geoprocessing
framework on which LM and LP are built. For an introduction to this
framework please refer to ESRI’s Geoprocessing Help. For ArcMap the URL
is
https://desktop.arcgis.com/en/arcmap/latest/analyze/main/what-is-geoprocessing.htm
and for ArcGIS Pro the URL is
https://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/basics/what-is-geoprocessing-.htm.

Coding Conventions
==================

As a Python project, developers are encouraged to follow the PEP8 style
guide (https://www.python.org/dev/peps/pep-0008/). Please note the
following conventions:

-  Class, method, function and variable names – lowercase with
   underscore separators (e.g. function_name()).

-  Constant “variable” names – all uppercase (e.g. CONSTANT).

-  Maximum line length – 79 characters.

LP Code Organization
====================

ArcGIS is flexible with regards to the installation location of custom
toolboxes like Linkage Mapper. However, Linkage Mapper expects all
Python files (files with .py extension) to be in a subdirectory called
“scripts”.

Most of the LP functionality is defined in two Python modules –
lp_main.py and lp_settings.py. The LP ArcGIS tool calls and passes the
input parameters to lp_main.py.

lp_settings.py
--------------

A module containing “constants” representing advanced LP
settings/parameters that are not included in the tool dialog.

lp_main.py
----------

The primary LP module, which includes:

-  The execution starting point (if \__name_\_ == "__main_\_ "), which
   calls the main() controlling function.

-  The main() controlling function.

-  Functions for the preparation steps.

-  The run_analysis() function and numerous called functions, which
   implement the primary analysis logic. The called functions are
   organized as per the Geoprocessing Summary below.

-  Local helper functions.

-  All functions are described in the LP Classes and Functions section
   below.

Summary Diagram of all the modules
----------------------------------

-  On the following page there is a summary diagram of all the modules
   in the Linkage Mapper toolbox (including those unrelated to Linkage
   Priority).

-  It gives a good overview of dependencies.

-  It was created using the Pyreverse package.

Linkage Mapper.tbx
------------------

This file defines the Linkage Mapper ArcGIS toolbox. It is modified by
right-clicking on it in ArcMap or ArcCatalog and selecting:

-  Item Description, to view the tool metadata (including help text) and
   edit it.

-  Properties, to define the tool’s:

   -  Name

   -  Label

   -  Description

   -  Optional underlying stylesheet

   -  Underlying .py script file

   -  Parameters (the type and order of these must match the order in
         which they are processed in the code)

   -  Optional validation code to be run before the .py script is called

   -  Optional compiled help file

In general, the toolbox should only be modified when there are new
tools, new parameters for existing tools or updated help text.

LpDlgContent.xsl
----------------

This file defines the stylesheet used by the Linkage Priority tool. It
facilitates group labeling and nesting of parameters in the tool dialog.
It only works for ArcGIS Desktop.

.. image:: lp_dev/image1.png
   :width: 6.40486in
   :height: 9.44306in

Geoprocessing Summary
=====================

The LP User Guide includes a geoprocessing overview. Additional details
are provided here.

-  Check that LM in the same Project Directory successfully finished
   Steps 3 and 5, and terminate if issues are encountered

-  Make preliminary calculations for each corridor

   -  Calculate Permeability

      -  In project_LCPs line feature class, calculate the attribute
         Raw_Perm as LCP_Length / CW_Dist

      -  In project_LCPs line feature class, calculate the attribute
         Rel_Perm as a normalization of all Raw_Perm values

   -  Calculate Relative Closeness

      -  In project_LCPs line feature class, calculate the attribute
         Rel_Close as a normalization of all LCP_Length values

-  Calculate Core Area Value (CAV) and its components for each core

   -  Check weights and warn if issues

   -  Add and calculate attributes in the input Core Area Feature Class

      -  Mean resistance: mean_res

      -  Normalized resistance: norm_res

      -  Size: area

      -  Normalized size: norm_size

      -  Perimeter: perimeter

      -  Area/perimeter ratio: ap_ratio

      -  Normalized area/perimeter ratio: norm_ratio

      -  [Optional] Other core area value: ocav

      -  [Optional] Normalized other core area value: nocav

      -  [Optional] Expert core area value: ecav

      -  [Optional] Normalized expert core area value: necav

      -  [Optional] Current Flow Centrality value (from Centrality
         Mapper): CF_Central

      -  [Optional] Normalized CF_Central value: ncfc

      -  Core area value: cav

         -  (norm_res \* Resistance Weight) +

..

   (norm_size \* Size Weight) +\_

   (norm_ratio \* Area/Perimeter Weight) +

   (necav \* Expert Core Area Value Weight) +

   (ncfc \* Current Flow Centrality Weight) +

   (nocav \* Other Core Area Value Weight)

-  Normalized core area value: norm_cav

-  [Optional] Calculate Corridor Specific Value and Blended Priority
   raster

   -  Calculate corridor specific priority (CSP) raster for each
      corridor

      -  Check weights and warn if issues

      -  Normalize Expert Corridor Importance Value: neciv

   -  [Optional] Calculate Climate Linkage Priority Value for each core
         area

      -  Current climate envelope: cclim_env

         -  [Optional] Calculate the mean values of a raster within each
               core area: fclim_env

      -  Calculate and save climate ratios to LCP layer and include
            start core and destination

      -  Save Climate Analog Linkage Priority Value (A) and Climate
            Preference Linkage Priority Value (L) for each core pair to
            LCP Layer

      -  Normalize climate priority values (A & L) for each core pair

      -  Combine climate priority values A & L in a weighted sum to
            yield Core Areas Climate Linkage Priority Value (O):
            Clim_Lnk_Priority

   -  Average the core area value of the two cores in the corridor:
         avg_cav

   -  Calculate CSP raster:

      -  (Rel_Close \* Closeness Weight) + (Rel_Perm \* Permeability
            Weight) +

..

   (avg_cav \* Core Area Value Weight) + (neciv \* Expert Corridor
   Importance Value Weight) + (Clim_Lnk_Priority \* Climate Envelope
   Difference Weight)

-  Normalize CSP values

-  [Optional] Flag low quality corridors not to use

-  [Optional] Create blended priority raster

   -  For each CSP raster

-  [Optional] Save a copy of Cores as the "Output for ModelBuilder
   Precondition"

LP Functions
============

.. _lp_main.py-1:

lp_main.py
----------

**add_output_path**\ (in_str)

   Append LinkMap GDB path to inputted value.

**blended_priority**\ (rast_list, lcp_ncsp)

   Calculate overall Blended Priority.

**calc_blended_priority**\ (lcp_lines)

   Generate Blended Priority raster from NLCC rasters.

**calc_cav**\ (core_lyr)

   Calculate Core Area Value (CAV) and its components for each core.

**calc_closeness**\ (lcp_lines)

   Calculate relative closeness for each Least Cost Path.

**calc_csp**\ (lcp_lines, core_lyr)

   Calculate Corridor Specific Priority (CSP) for each linkage.

**calc_permeability**\ (lcp_lines)

   Calculate raw and relative permeability for each Least Cost Path.

**check_add_field**\ (feature_class, field_name, data_type)

   Check if field exists, and if not then add.

**chk_cav_wts**\ ()

   Check weights used in CAV calculation.

**chk_csp_wts**\ ()

   Check weights used in CSP calculation.

**chk_lnk_tbls**\ ()

   Check that LM finished with steps 3 and 5.

**clim_env_read**\ (core_lyr, core, field)

   Read core climate envelope.

**clim_envelope**\ (core_lyr)

   Determine Climate Envelope for each core.

**clim_linkage_priority**\ (lcp_lines, core_lyr)

   Calculate Core Areas Climate Linkage Priority Value.

**clim_lnk_value**\ (xlnk, min_pnt, target_pnt, max_pnt)

   Calculate climate linkage value using equation of straight line.

**clim_priority_combine**\ (lcp_lines)

   | Combine climate priority (A & L) values.
   |  
   | Combine climate priority values A & L in a weighted sum to yield Core
   | Areas Climate Linkage Priority Value (O).

**clim_priority_val_normal**\ (lcp_lines)

   Normalize climate priority values (A & L) for each core pair.

**clim_priority_values**\ (lcp_lines)

   | Save climate priority values for each core pair to LCP layer.
   |  
   | Save Climate Analog Linkage Priority Value (A) and
   | Climate Preference Linkage Priority Value (L) for each core pair
   | to LCP Layer.

**clim_ratios**\ (lcp_lines, core_lyr)

   | Calculate and save climate ratios to LCP layer.
   |  
   | Calculate and save climate ratios to LCP layer and include start core 

   and destination.

**clip_nlcc_to_threashold**\ (lcp_list)

   | Clip NLCC_A_B rasters to CWD threshold.
   |  
   | Clip the normalized least cost corridors using the specified CWD
   | Threshold.

**core_mean**\ (in_rast, core_lyr, in_var)

   Calculate the mean values of a raster within each core area.

**create_run_gdbs**\ ()

   Create scratch and if necessary intermediate GDB.

**eciv**\ ()

   Normalize Expert Corridor Importance Value (ECIV) for each corridor.

**get_lcp_fc**\ ()

   Get LCP feature class. Raise error if not found.

**get_lm_params**\ (argv)

   Get settings from Linkage Pathways inputs.

**intercept**\ (point, slope_val)

   | Find the intercept of a straight line.
   |  
   | Where (x,y) is a point on the line and b is the slope of the line.

**inv_norm**\ (rast_list)

   Invert and normalize each corridor.

**lcp_csp_for_bp**\ (lcp_lines)

   Get list of LCPs and their normalized CSP values for BP raster 

   | creation.
   |  
   | Filter LCPs based on CPS cutoff if applicable. Return list with LCP
   | filenames and dictionary with LCP GDB filename as key and normalized

   CSP as value.

**log_setup**\ ()

   Set up Linkage Mapper logging.

**main**\ (argv=None)

   Run Linkage Priority tool.

**make_core_lyr**\ ()

   | Create feature layer from cores feature class.
   |  
   | Raise error if core feature class is not found.

**normalize_field**\ (in_table, in_field, out_field,
normalization_method='MAX_VALUE', invert=False)

   | Normalize values in in_field into out_field.
   |  
   | Normalize values in in_field into out_field using score range or max
   | score method, with optional inversion.

**normalize_raster**\ (in_raster, normalization_method='MAX_VALUE',
invert=False)

   | Normalize values in in_raster.
   |  
   | Normalize values in in_raster using score range or max score method,
   | with optional inversion.

**read_lm_params**\ (proj_dir)

   Read Linkage Pathways input parameters from log file.

**run_analysis**\ ()

   Run main Linkage Priority analysis.

**save_interm_rast**\ (rast_list, base_name)

   Save intermediate rasters if user chooses.

**sline_y_value**\ (x_coord, slope_val, intercept_val)

   | For a x value on a straight line find its corresponding y value.
   |  
   | The equation of a straight line is: y = mx + b
   | where m is the slope of the line and b is the intercept.

**slope**\ (point1, point2)

   | Calculate slope of a straight line.
   |  
   | Where (x1,y1) and (x2,y2) are points on the line.

**value_range**\ (layer, field)

   Get value range of field in layer.

LM Architecture
===============

As detailed above, LP modifies and builds on the standard LM outputs
using the storage structure established by LM. As part of the LM family
of tools, LP also takes advantage of some shared elements of the LM
architecture.

Configuration and Settings
--------------------------

For accessing the details of the successful LM run that LP builds on, LP
instantiates and fills the lm_config() class (defined in lm_config.py)
as lm_env. This includes access to LM’s advanced settings defined in
lm_settings.py.

Logging
-------

LM provides logging to both the ArcGIS geoprocessing framework (for
display and geoprocessing results history within ArcGIS) and to text
files within the LM project structure (in the run_history folder). LP
uses the following functions logging functions from lm_util.py:

**create_log_file**\ (messageDir, toolName, inParameters):

   Creates and new text file for logging and remembers it for the
   current run.

**write_log**\ (string):

Write the string to the current log file.

**close_log**\ \_file():

Write the current time to the current log file and close the file.

**gprint**\ (string):

   Write the string to the current log file and pass to the ArcGIS
   geoprocessing framework as a message or warning.

**raise_error**\ (msg):

   Write the message to the current log file, pass it to the ArcGIS
   geoprocessing framework as an error, and close the log file.

Other Utilities
---------------

LP also uses the following functions from lm_util.py:

**build_stats**\ (raster):

   Builds statistics and pyramids for output rasters.

**delete_data**\ (dataset):

   Delete the passed ArcGIS dataset.

Other Notes
===========

Source Control Using GitHub
---------------------------

The LM family of tools are managed as an open source repository on
GitHub. The repository URL is
https://github.com/linkagescape/linkage-mapper.

Debugging
---------

For information on how to debug script tools in ArcGIS Desktop see
ESRI’s ArcGIS *Debugging script tools* help page
(https://desktop.arcgis.com/en/arcmap/latest/analyze/creating-tools/debugging-script-tools.htm)
and for ArcGIS Pro see the *Debug Python code* help page
(https://pro.arcgis.com/en/pro-app/arcpy/get-started/debugging-python-code.htm).

Becoming a Linkage Mapper Contributor
-------------------------------------

We encourage contributions to the LM project by ArcGIS/Python
developers. This could include enhancements and fixes to existing tools,
and development of new tools for the LM toolbox. We encourage new tools
to follow the protocols in Linkage Priority and Climate Linkage Mapper,
which are currently the two newest tools in the LM toolbox.

Future Enhancements
-------------------

As with any active software project, there have been numerous
suggestions for future enhancements. Please use the LM User Group (see
the Support section of the LM User Guide) to register your suggestions.
