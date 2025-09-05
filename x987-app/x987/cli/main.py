"""
Main CLI module for View-from-CSV

PROVIDES: Argument parsing and command routing for pipeline commands
DEPENDS: x987.config:get_config, x987.utils.log:setup_logging, x987.doctor:run_doctor, x987.pipeline:get_pipeline_runner
CONSUMED BY: x987.__main__:main function
CONTRACT: Provides main CLI interface with subcommands for pipeline steps
TECH CHOICE: argparse with subcommands for pipeline orchestration
RISK: Low - CLI interface is straightforward
"""

import argparse
import sys
import signal
import time
import traceback
from pathlib import Path
from typing import Optional

from ..config import get_config, get_timestamp_run_id
from ..utils.log import setup_logging, get_logger
from ..doctor import run_doctor
from ..pipeline import get_pipeline_runner
# Removed dependency on old report modules
# Removed dependency on csv_io module
from .utils import with_timeout, TimeoutError

logger = get_logger("cli.main")

def cmd_doctor(args):
    """Run system diagnostics"""
    print("🔍 Running system diagnostics...")
    logger.info("Running system diagnostics...")
    try:
        success = run_doctor()
        if success:
            print("✅ System diagnostics completed successfully")
            logger.info("System diagnostics completed successfully")
            return 0
        else:
            print("❌ System diagnostics failed")
            logger.error("System diagnostics failed")
            return 1
    except Exception as e:
        print(f"❌ System diagnostics error: {e}")
        logger.error(f"System diagnostics error: {e}")
        return 1

def cmd_collect(args):
    """Run collection step"""
    print("📡 Running collection step...")
    logger.info("Running collection step...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Run just the collection step
        run_kwargs = {'verbose': args.verbose}
        if getattr(args, 'headful', False):
            run_kwargs['headful'] = True
        result = runner.run_single_step("collection", config, **run_kwargs)
        
        if result.is_success:
            urls = result.data
            print(f"✅ Collection completed: {len(urls)} URLs found")
            print(f"📊 Output: {len(urls)} vehicle listing URLs collected")
            logger.info(f"Collection completed: {len(urls)} URLs found")
            return 0
        else:
            print(f"❌ Collection failed: {result.error}")
            logger.error(f"Collection failed: {result.error}")
            return 1
            
    except Exception as e:
        print(f"❌ Collection error: {e}")
        logger.error(f"Collection error: {e}")
        return 1

def cmd_scrape(args):
    """Run scraping step"""
    print("🕷️  Running scraping step...")
    logger.info("Running scraping step...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Run just the scraping step
        run_kwargs = {'verbose': args.verbose}
        if getattr(args, 'headful', False):
            run_kwargs['headful'] = True
        result = runner.run_single_step("scraping", config, **run_kwargs)
        
        if result.is_success:
            results = result.data
            print(f"✅ Scraping completed: {len(results)} results")
            print(f"📊 Output: {len(results)} vehicle records scraped")
            logger.info(f"Scraping completed: {len(results)} results")
            return 0
        else:
            print(f"❌ Scraping failed: {result.error}")
            logger.error(f"Scraping failed: {result.error}")
            return 1
            
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        logger.error(f"Scraping error: {e}")
        return 1

def cmd_transform(args):
    """Run transform step"""
    print("🔄 Running transform step...")
    logger.info("Running transform step...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Run just the transformation step
        result = runner.run_single_step("transformation", config, verbose=args.verbose)
        
        if result.is_success:
            results = result.data
            print(f"✅ Transform completed: {len(results)} results")
            print(f"📊 Output: {len(results)} transformed vehicle records")
            logger.info(f"Transform completed: {len(results)} results")
            return 0
        else:
            print(f"❌ Transform failed: {result.error}")
            logger.error(f"Transform failed: {result.error}")
            return 1
            
    except Exception as e:
        print(f"❌ Transform error: {e}")
        logger.error(f"Transform error: {e}")
        return 1

def cmd_dedupe(args):
    """Run deduplication step"""
    print("🔄 Running deduplication step...")
    logger.info("Running deduplication step...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Run just the deduplication step
        result = runner.run_single_step("deduplication", config, verbose=args.verbose)
        
        if result.is_success:
            results = result.data
            print(f"✅ Deduplication completed: {len(results)} results")
            print(f"📊 Output: {len(results)} unique vehicle records")
            logger.info(f"Deduplication completed: {len(results)} results")
            return 0
        else:
            print(f"❌ Deduplication failed: {result.error}")
            logger.error(f"Deduplication failed: {result.error}")
            return 1
            
    except Exception as e:
        print(f"❌ Deduplication error: {e}")
        logger.error(f"Deduplication error: {e}")
        return 1

def cmd_fair_value(args):
    """Run fair value calculation step"""
    print("💰 Running fair value calculation step...")
    logger.info("Running fair value calculation step...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Run just the fair value step
        result = runner.run_single_step("fair_value", config, verbose=args.verbose)
        
        if result.is_success:
            results = result.data
            print(f"✅ Fair value calculation completed: {len(results)} results")
            print(f"📊 Output: {len(results)} vehicles with calculated fair values")
            logger.info(f"Fair value calculation completed: {len(results)} results")
            return 0
        else:
            print(f"❌ Fair value calculation failed: {result.error}")
            logger.error(f"Fair value calculation failed: {result.error}")
            return 1
            
    except Exception as e:
        print(f"❌ Fair value calculation error: {e}")
        logger.error(f"Fair value calculation error: {e}")
        return 1

def cmd_rank(args):
    """Run ranking step"""
    print("🏆 Running ranking step...")
    logger.info("Running ranking step...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Run just the ranking step
        result = runner.run_single_step("ranking", config, verbose=args.verbose)
        
        if result.is_success:
            results = result.data
            print(f"✅ Ranking completed: {len(results)} results")
            print(f"📊 Output: {len(results)} vehicles ranked by deal quality")
            logger.info(f"Ranking completed: {len(results)} results")
            return 0
        else:
            print(f"❌ Ranking failed: {result.error}")
            logger.error(f"Ranking failed: {result.error}")
            return 1
            
    except Exception as e:
        print(f"❌ Ranking error: {e}")
        logger.error(f"Ranking error: {e}")
        return 1

def cmd_pipeline(args):
    """Run complete pipeline"""
    print("🚀 Running complete pipeline...")
    logger.info("Running complete pipeline...")
    try:
        config = get_config()
        print(f"📁 Config file: {config.config_file}")
        
        # Get pipeline runner
        runner = get_pipeline_runner()
        
        # Show pipeline information
        info = runner.get_pipeline_info()
        print(f"📋 Pipeline steps: {', '.join(info['steps'])}")
        print(f"🔄 Execution order: {', '.join(info['execution_order'])}")
        
        # Run the complete pipeline
        run_kwargs = {'verbose': args.verbose}
        if getattr(args, 'headful', False):
            run_kwargs['headful'] = True
        result = runner.run_pipeline(config, **run_kwargs)
        
        print("✅ Complete pipeline completed successfully")
        
        # Extract the actual data from pipeline results
        pipeline_results = result.get('pipeline_results', {})
        if pipeline_results:
            # Get the final step result (ranking)
            ranking_result = pipeline_results.get('ranking')
            if ranking_result and ranking_result.is_success:
                final_data = ranking_result.data
                if isinstance(final_data, dict) and 'ranked_data' in final_data:
                    vehicle_count = len(final_data['ranked_data'])
                    print(f"📊 Final output: {vehicle_count} processed vehicles")
                else:
                    print(f"📊 Final output: {len(final_data) if isinstance(final_data, list) else 'Unknown'} processed vehicles")
            else:
                print("📊 Final output: Pipeline completed but no ranking data available")
        else:
            print("📊 Final output: No pipeline results available")
            
        logger.info("Complete pipeline completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        logger.error(f"Pipeline error: {e}")
        return 1

# Removed: cmd_view (modular view removed)

def cmd_view_step(args):
    """Run ONLY the current View pipeline step using latest CSV outputs"""
    print("🔍 Displaying modular data...")
    logger.info("Displaying modular data (view-step)...")
    try:
        # Build minimal previous_results so dependencies are considered met
        from ..pipeline.steps.base import StepResult, StepStatus
        from ..pipeline.steps.view import VIEW_STEP
        from datetime import datetime
        from pathlib import Path
        import glob
        
        # Load latest transformed CSV and ranking_main CSV as if prior steps succeeded
        results_dir = Path("x987-data/results")
        timestamp = args.timestamp
        if not timestamp:
            files = glob.glob(str(results_dir / "ranking_main_*.csv"))
            if files:
                files.sort()
                latest = Path(files[-1]).name
                timestamp = latest.replace("ranking_main_", "").replace(".csv", "")
        
        if not timestamp:
            print("❌ No results found to display")
            return 1
        
        # Fabricate success StepResults for dependencies
        now = datetime.now()
        prev = {
            'transformation': StepResult(step_name='transformation', status=StepStatus.COMPLETED, start_time=now, end_time=now, data={}),
            'ranking': StepResult(step_name='ranking', status=StepStatus.COMPLETED, start_time=now, end_time=now, data={})
        }
        
        # Load ranked_data into the shape view expects
        import csv
        import re
        ranked_file = results_dir / f"ranking_main_{timestamp}.csv"
        ranked_data = []
        def to_int(val):
            if val is None:
                return None
            try:
                s = str(val)
                s = re.sub(r"[^0-9\-]", "", s)
                return int(s) if s not in ("", "-") else None
            except Exception:
                return None

        with open(ranked_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize numeric fields from CSV strings
                for num_field in [
                    'asking_price_usd', 'deal_delta_usd', 'fair_value_usd',
                    'mileage', 'year'
                ]:
                    if num_field in row:
                        val = to_int(row.get(num_field))
                        row[num_field] = val if val is not None else row.get(num_field)
                ranked_data.append(row)
        
        prev['ranking'].data = {'ranked_data': ranked_data}
        
        # Run the view step directly
        config = {}
        result = VIEW_STEP.execute(config, prev)
        if result.is_success:
            logger.info("View-step displayed successfully")
            return 0
        else:
            print(f"❌ View-step failed: {result.error}")
            return 1
    except Exception as e:
        print(f"❌ Error running view-step: {e}")
        logger.error(f"Error running view-step: {e}")
        return 1

def cmd_transform_step(args):
    """Run from TRANSFORMATION onward using the latest scraping CSV as input"""
    print("🔄 Displaying transformation-forward pipeline (using latest scraping CSV)...")
    logger.info("Displaying transformation-forward pipeline (transform-step)...")
    try:
        from ..pipeline.steps.base import StepResult, StepStatus
        from ..pipeline.steps.transformation import TRANSFORMATION_STEP
        from ..pipeline.steps.deduplication import DEDUPLICATION_STEP
        from ..pipeline.steps.fair_value import FAIR_VALUE_STEP
        from ..pipeline.steps.ranking import RANKING_STEP
        from ..pipeline.steps.view import VIEW_STEP
        from ..config import get_config
        from datetime import datetime
        from pathlib import Path
        import glob, csv, sys

        # Resolve config dict (ensure required keys for steps like 'pipeline' and 'fair_value')
        cfg = get_config()
        config = cfg.config if hasattr(cfg, 'config') else cfg

        # Locate latest scraping CSV (or use provided --timestamp)
        results_dir = Path("x987-data/results")
        timestamp = args.timestamp
        if not timestamp:
            files = glob.glob(str(results_dir / "scraping_detailed_*.csv"))
            if files:
                files.sort()
                latest = Path(files[-1]).name
                timestamp = latest.replace("scraping_detailed_", "").replace(".csv", "")

        if not timestamp:
            print("❌ No scraping_detailed_*.csv results found to start from transformation")
            return 1

        scraping_file = results_dir / f"scraping_detailed_{timestamp}.csv"
        if not scraping_file.exists():
            print(f"❌ Scraping CSV not found: {scraping_file}")
            return 1

        print(f"📄 Using scraping CSV: {scraping_file}")

        # Increase CSV field size limit for large raw_html fields
        try:
            max_int = sys.maxsize
            while True:
                try:
                    csv.field_size_limit(max_int)
                    break
                except OverflowError:
                    max_int = int(max_int / 10)
                    if max_int < 10_000_000:
                        csv.field_size_limit(10_000_000)
                        break
        except Exception:
            pass

        # Load scraping data rows
        scraping_data = []
        with open(scraping_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                scraping_data.append(row)

        now = datetime.now()
        prev = {
            'scraping': StepResult(step_name='scraping', status=StepStatus.COMPLETED, start_time=now, end_time=now, data={})
        }
        prev['scraping'].data = {
            'scraping_data': scraping_data
        }

        # Execute transformation forward (pricing-mode aware)
        from ..config import get_config as _get_cfg
        pmode = _get_cfg().get_pricing_mode() if hasattr(_get_cfg(), 'get_pricing_mode') else 'msrp_only'
        pipeline_str = "transformation → deduplication → ranking → view" if pmode == 'msrp_only' else "transformation → deduplication → fair_value → ranking → view"
        print(f"\n🔄 Executing: {pipeline_str}")
        tr_result = TRANSFORMATION_STEP.execute(config, prev)
        if not tr_result or not tr_result.is_success:
            print(f"❌ Transformation failed: {tr_result.error if tr_result else 'unknown error'}")
            return 1
        prev['transformation'] = tr_result

        # Execute deduplication
        dd_result = DEDUPLICATION_STEP.execute(config, prev)
        if not dd_result or not dd_result.is_success:
            print(f"❌ Deduplication failed: {dd_result.error if dd_result else 'unknown error'}")
            return 1
        prev['deduplication'] = dd_result

        # Execute fair_value only if not MSRP-only mode
        if pmode != 'msrp_only':
            fv_result = FAIR_VALUE_STEP.execute(config, prev)
            if not fv_result or not fv_result.is_success:
                print(f"❌ Fair value failed: {fv_result.error if fv_result else 'unknown error'}")
                return 1
            prev['fair_value'] = fv_result

        # Execute ranking
        rk_result = RANKING_STEP.execute(config, prev)
        if not rk_result or not rk_result.is_success:
            print(f"❌ Ranking failed: {rk_result.error if rk_result else 'unknown error'}")
            return 1
        prev['ranking'] = rk_result

        # Execute view (display)
        vw_result = VIEW_STEP.execute({}, prev, verbose=args.verbose)
        if vw_result and getattr(vw_result, 'is_success', False):
            logger.info("Transform-step completed through view successfully")
            return 0
        else:
            print("⚠️  View did not display data (but prior steps completed)")
            return 0

    except Exception as e:
        print(f"❌ Error running transform-step: {e}")
        logger.error(f"Error running transform-step: {e}")
        return 1

def cmd_info(args):
    """Show pipeline information"""
    print("ℹ️  Pipeline Information")
    logger.info("Showing pipeline information...")
    try:
        runner = get_pipeline_runner()
        info = runner.get_pipeline_info()
        
        print(f"📋 Available steps: {', '.join(info['steps'])}")
        print(f"🔄 Execution order: {', '.join(info['execution_order'])}")
        
        # Show step details
        print("\n📝 Step Details:")
        for step_name in info['steps']:
            step = runner.get_step(step_name)
            if step:
                print(f"  • {step_name}: {step.get_description()}")
                deps = step.get_dependencies()
                if deps:
                    print(f"    Dependencies: {', '.join(deps)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting pipeline info: {e}")
        logger.error(f"Error getting pipeline info: {e}")
        return 1

def cmd_config(args):
    """Show configuration information"""
    print("⚙️  Configuration Information")
    logger.info("Showing configuration information...")
    try:
        config = get_config()
        summary = config.get_config_summary()
        
        print(f"📁 Config file: {summary['config_file']}")
        print(f"🏷️  Pricing mode: {summary.get('pricing_mode', 'msrp_only')}")
        print(f"🔍 Search URLs: {summary['search_urls_count']}")
        print(f"🕷️  Scraping concurrency: {summary['scraping_concurrency']}")
        print(f"⏱️  Polite delay: {summary['scraping_polite_delay_ms']}ms")
        if str(summary.get('pricing_mode', 'msrp_only')).lower() != 'msrp_only' and summary.get('fair_value_base') is not None:
            print(f"💰 Fair value base: ${summary['fair_value_base']:,}")
        print(f"🔧 Options enabled: {summary['options_enabled']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting config info: {e}")
        logger.error(f"Error getting config info: {e}")
        return 1

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="View-from-CSV: Vehicle data extraction and analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m x987 pipeline          # Run complete pipeline
  python -m x987 collect           # Run collection step only
  python -m x987 scrape            # Run scraping step only
  python -m x987 transform         # Run transformation step only
  python -m x987 view-step         # Display final ranked view from latest results
  python -m x987 info              # Show pipeline information
  python -m x987 config            # Show configuration
  python -m x987 doctor            # Run system diagnostics
        """
    )
    
    parser.add_argument(
        'command',
        choices=['pipeline', 'collect', 'scrape', 'transform', 'dedupe', 'fair_value', 'rank', 'view-step', 'transform-step', 'info', 'config', 'doctor'],
        help='Pipeline command to execute'
    )
    
    parser.add_argument(
        '--headful',
        action='store_true',
        help='Use headful mode for browser automation (default: True)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # Removed: --export-html (HTML export removed)
    
    # Optional timestamp for view-step (define BEFORE parsing)
    parser.add_argument(
        '--timestamp',
        type=str,
        help='Timestamp suffix to pick specific results (e.g., 20250826_133714)'
    )

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.verbose)
    
    # Command routing

    commands = {
        'pipeline': cmd_pipeline,
        'collect': cmd_collect,
        'scrape': cmd_scrape,
        'transform': cmd_transform,
        'dedupe': cmd_dedupe,
        'fair_value': cmd_fair_value,
        'rank': cmd_rank,
        # Removed: 'view' (modular view removed)
        'view-step': cmd_view_step,
        'transform-step': cmd_transform_step,
        'info': cmd_info,
        'config': cmd_config,
        'doctor': cmd_doctor
    }
    
    try:
        exit_code = commands[args.command](args)
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            traceback.print_exc()
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
