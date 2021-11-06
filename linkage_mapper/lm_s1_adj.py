""" Step 1: Get adjacencies.

Determines adjacencies between core areas in either or both Euclidean and
cost-weighted distance space

"""

from os import path
import shutil

# Add support for Python 2. Try to import Python 3 modules first.
try:
    from time import perf_counter
except ImportError:
    from time import clock as perf_counter

import numpy as npy
import arcpy

from lm_config import tool_env as cfg
import lm_util as lu


_SCRIPT_NAME = "lm_s1_adj.py"

gprint = lu.gprint


def STEP1_get_adjacencies():
    """Determines adjacencies between core areas in either or both
    Euclidean and cost-weighted distance space.

    """
    try:
        lu.dashline(1)
        gprint('Running script ' + _SCRIPT_NAME)

        # Remove adj directory and files from previous runs
        lu.delete_dir(cfg.ADJACENCYDIR)
        lu.delete_file(cfg.CWDADJFILE)
        lu.delete_file(cfg.EUCADJFILE)

        if not cfg.S2ADJMETH_CW and not cfg.S2ADJMETH_EU:
            # Adjacency not needed
            return

        lu.create_dir(cfg.ADJACENCYDIR)
        wrk_sp = lu.set_scratch_wksp('step1')

        gprint('Adjacency files will be written to ' +
                cfg.ADJACENCYDIR)

        arcpy.env.pyramid = "NONE"
        arcpy.env.rasterStatistics = "NONE"

        if cfg.BUFFERDIST is not None:
            gprint('Reducing processing area using bounding circle '
                   'plus buffer of ' +
                   str(float(cfg.BUFFERDIST)) + ' map units')
            bnd_cir = lu.create_bnd_circle(cfg.COREFC, cfg.BUFFERDIST, wrk_sp)
        else:
            bnd_cir = None

        if cfg.S1ADJMETH_CW:
            cwadjacency(bnd_cir)
        if cfg.S1ADJMETH_EU:
            euadjacency(bnd_cir)

        lu.del_keep_inter_data(bnd_cir)
        lu.del_keep_inter_dir(wrk_sp)

    # Return GEOPROCESSING specific errors
    except arcpy.ExecuteError:
        lu.dashline(1)
        gprint('****Failed in step 1. Details follow.****')
        lu.exit_with_geoproc_error(_SCRIPT_NAME)

    # Return any PYTHON or system specific errors
    except Exception:
        lu.dashline(1)
        gprint('****Failed in step 1. Details follow.****')
        lu.exit_with_python_error(_SCRIPT_NAME)
    return


def cwadjacency(bnd_cir=None):
    """Calculate cost-weighted adjacency."""
    try:
        gprint('\nCalculating cost-weighted distance adjacency')
        PREFIX = cfg.PREFIX

        # May need to set extent prior to core poly to raster conversion...
        # ----------------------------------------------
        # Cost-weighted allocation code
        arcpy.env.cellSize = arcpy.Describe(cfg.RESRAST).MeanCellHeight
        arcpy.env.extent = arcpy.Describe(cfg.RESRAST).extent
        if bnd_cir is not None:
            # Clip resistance raster using bounding circle
            start_time = perf_counter()
            arcpy.env.cellSize = arcpy.Describe(cfg.RESRAST).MeanCellHeight
            arcpy.env.extent = arcpy.Describe(cfg.RESRAST).Extent
            bResistance = arcpy.sa.ExtractByMask(cfg.RESRAST, bnd_cir)
            gprint('\nReduced resistance raster extracted using '
                   'bounding circle.')
            lu.print_elapsed_time(start_time)
        else:
            bResistance = cfg.RESRAST

        start_time = perf_counter()
        gprint('Starting cost-weighted distance allocation...')

        if cfg.TMAXCWDIST is not None:
            gprint('Maximum cost-weighted distance set to ' +
                              str(cfg.TMAXCWDIST))
        arcpy.env.cellSize = arcpy.Describe(bResistance).MeanCellHeight
        arcpy.env.extent = "MAXOF"
        gprint('Processing cell size: ' + arcpy.env.cellSize)

        arcpy.CreateFileGDB_management(cfg.OUTPUTDIR, path.basename(cfg.CWDGDB))
        outDistanceRaster = path.join(cfg.CWDGDB, PREFIX + "_cwd")
        alloc_ras = path.join(cfg.ADJACENCYDIR, 'CWD_alloc_ras')

        costAllocOut = arcpy.sa.CostAllocation(
                cfg.CORERAS, bResistance, cfg.TMAXCWDIST,
                cfg.CORERAS, "VALUE", outDistanceRaster)
        costAllocOut.save(alloc_ras)

        gprint('\nBuilding output statistics and pyramids for CWD raster.')
        lu.build_stats(outDistanceRaster)
        gprint('Cost-weighted distance allocation done.')
        lu.print_elapsed_time(start_time)
        adjshiftwrite(alloc_ras, cfg.CWDADJFILE, lu.set_scratch_wksp('step1\cwd'))

    # Return GEOPROCESSING specific errors
    except arcpy.ExecuteError:
        lu.dashline(1)
        gprint('****Failed in step 1. Details follow.****')
        lu.exit_with_geoproc_error(_SCRIPT_NAME)

    # Return any PYTHON or system specific errors
    except Exception:
        lu.dashline(1)
        gprint('****Failed in step 1. Details follow.****')
        lu.exit_with_python_error(_SCRIPT_NAME)


def euadjacency(bnd_cir=None):
    """Calculate Euclidean adjacency."""
    try:
        lu.dashline()
        gprint('Calculating Euclidean adjacency')
        wrk_space = lu.set_scratch_wksp('step1\euc')

        # ----------------------------------------------
        # Euclidean allocation code
        gprint('Starting Euclidean adjacency processing...')
        # Euclidean cell size
        cellSizeEuclidean = arcpy.Describe(cfg.RESRAST).MeanCellHeight

        oldextent = arcpy.env.extent
        if bnd_cir is not None:
            arcpy.env.extent = arcpy.Describe(bnd_cir).extent

        start_time = perf_counter()

        outDistanceRaster = path.join(wrk_space, 'euc')
        alloc_ras = path.join(cfg.ADJACENCYDIR, 'Euc_alloc_ras')

        alloc_raster = arcpy.sa.EucAllocation(
                cfg.CORERAS, "", "", cellSizeEuclidean, "",
                outDistanceRaster, "")
        alloc_raster.save(alloc_ras)
        lu.del_keep_inter_data(outDistanceRaster)

        gprint('\nEuclidean distance allocation done.')
        lu.print_elapsed_time(start_time)
        arcpy.env.extent = oldextent
        adjshiftwrite(alloc_ras, cfg.EUCADJFILE, wrk_space)

    # Return GEOPROCESSING specific errors
    except arcpy.ExecuteError:
        lu.dashline(1)
        gprint('****Failed in step 1. Details follow.****')

        lu.exit_with_geoproc_error(_SCRIPT_NAME)

    # Return any PYTHON or system specific errors
    except Exception:
        lu.dashline(1)
        gprint('****Failed in step 1. Details follow.****')

        lu.exit_with_python_error(_SCRIPT_NAME)


def adjshiftwrite(araster, csv_file, wrk_space):
    """Get adjacencies using shift method and write to disk"""
    # To be replaced by getLeastCostDistsUsingShiftMethod if implemented
    adjTable = get_adj_using_shift_method(araster, wrk_space)
    lu.write_adj_file(csv_file, adjTable)
    log_file = path.join(cfg.LOGDIR,
        path.splitext(path.basename(csv_file))[0] + '_step1.csv')
    shutil.copyfile(csv_file, log_file)


def get_adj_using_shift_method(alloc, wrk_space):
    """Returns table listing adjacent core areas using a shift method.

    The method involves shifting the allocation grid one pixel and then looking
    for pixels with different allocations across shifted grids.

    """
    allocs = ['alloc_r', 'alloc_ul', 'alloc_ur', 'alloc_u']
    alloc_r, alloc_ul, alloc_ur, alloc_u = (
        path.join(wrk_space, x) for x in allocs)

    cellSize = arcpy.Describe(alloc).MeanCellHeight
    arcpy.env.cellSize = cellSize

    posShift = arcpy.env.cellSize
    negShift = -1 * float(arcpy.env.cellSize)

    gprint('Calculating adjacencies crossing allocation boundaries...')
    start_time = time.clock()

    arcpy.Shift_management(alloc, alloc_r, posShift, "0")
    adjTable_r = get_allocs_from_shift(alloc, alloc_r)
    arcpy.Shift_management(alloc, alloc_ul, negShift, posShift)
    adjTable_ul = get_allocs_from_shift(alloc, alloc_ul)
    arcpy.Shift_management(alloc, alloc_ur, posShift, posShift)
    adjTable_ur = get_allocs_from_shift(alloc, alloc_ur)
    arcpy.Shift_management(alloc, alloc_u, "0", posShift)
    adjTable_u = get_allocs_from_shift(alloc, alloc_u)
    lu.del_keep_inter_data(alloc_r, alloc_ul, alloc_ur, alloc_u)

    lu.print_elapsed_time(start_time)

    adjTable = combine_adjacency_tables(adjTable_r, adjTable_u, adjTable_ur,
                                        adjTable_ul)

    return adjTable


def get_allocs_from_shift(alloc, alloc_sh):
    """Returns a table of adjacent allocation zones using grid shift method"""
    try:
        comb_ras = arcpy.sa.Combine([alloc, alloc_sh])
        allocLookupTable = get_alloc_lookup_table(comb_ras)
        lu.del_keep_inter_rast(comb_ras, "comb_ras")
        return allocLookupTable[:, 1:3]

    except arcpy.ExecuteError:
        lu.exit_with_geoproc_error(_SCRIPT_NAME)
    except Exception:
        lu.exit_with_python_error(_SCRIPT_NAME)


def get_alloc_lookup_table(combine_ras):
    """Returns a table of adjacent allocation zones.

    Requires a raster with allocation zone attributes.

    """
    try:
        fldlist = arcpy.ListFields(combine_ras)

        valFld = fldlist[1].name
        allocFld = fldlist[3].name
        allocFld_sh = fldlist[4].name

        allocLookupTable = npy.zeros((0, 3), dtype="int32")
        appendRow = npy.zeros((1, 3), dtype="int32")

        rows = arcpy.SearchCursor(combine_ras)
        row = next(rows)
        while row:
            alloc = row.getValue(allocFld)
            alloc_sh = row.getValue(allocFld_sh)
            if alloc != alloc_sh:
                appendRow[0, 0] = row.getValue(valFld)
                appendRow[0, 1] = alloc
                appendRow[0, 2] = alloc_sh
                allocLookupTable = npy.append(allocLookupTable, appendRow,
                                              axis=0)
            row = next(rows)
        del row
        del rows

        return allocLookupTable
    except arcpy.ExecuteError:
        lu.exit_with_geoproc_error(_SCRIPT_NAME)
    except Exception:
        lu.exit_with_python_error(_SCRIPT_NAME)


def combine_adjacency_tables(adjTable_r, adjTable_u, adjTable_ur, adjTable_ul):
    """Combines tables describing whether core areas are adjacent based on
    allocation zones that touch on horizontal, vertical, and diagonal axes
    """
    try:
        adjTable = npy.append(adjTable_r, adjTable_u, axis=0)
        adjTable = npy.append(adjTable, adjTable_ur, axis=0)
        adjTable = npy.append(adjTable, adjTable_ul, axis=0)

        pairs = npy.sort(adjTable[:, 0:2])
        adjTable[:, 0:2] = pairs

        # sort by 1st core Id then by 2nd core Id
        ind = npy.lexsort((adjTable[:, 1], adjTable[:, 0]))
        adjTable = adjTable[ind]

        numDists = len(adjTable)
        x = 1
        while x < numDists:
            if (adjTable[x, 0] == adjTable[x - 1, 0] and
                adjTable[x, 1] == adjTable[x - 1, 1]):
                adjTable[x - 1, 0] = 0  # mark for deletion
            x = x + 1

        if numDists > 0:
            delRows = npy.asarray(npy.where(adjTable[:, 0] == 0))
            delRowsVector = npy.zeros((delRows.shape[1]), dtype="int32")
            delRowsVector[:] = delRows[0, :]
            adjTable = lu.delete_row(adjTable, delRowsVector)
            del delRows
            del delRowsVector

        return adjTable
    except arcpy.ExecuteError:
        lu.exit_with_geoproc_error(_SCRIPT_NAME)
    except Exception:
        lu.exit_with_python_error(_SCRIPT_NAME)
