#!/usr/bin/env python3
"""
Shoob.gg Card Scraper - Main Execution Script
=============================================

Professional-grade web scraper for extracting card data from shoob.gg
with live-save functionality and resume capability.

Usage:
    python main.py                    # Scrape with default config settings
    python main.py --start 1 --end 5 # Scrape pages 1-5
    python main.py --resume           # Resume from where it left off
    python main.py --summary          # Show summary of scraped data

Author: Senior Developer
Version: 2.0.0
"""

import asyncio
import argparse
import sys
import warnings
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from scraper import ShoobCardScraper


def suppress_asyncio_warnings():
    """Suppress Windows-specific asyncio warnings that don't affect functionality."""
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed transport.*")
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*I/O operation on closed pipe.*")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Professional Shoob.gg Card Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Use config defaults
  python main.py --start 1 --end 10 # Scrape pages 1-10
  python main.py --resume            # Resume from existing data
  python main.py --summary           # Show data summary
        """
    )
    
    parser.add_argument(
        "--start",
        type=int,
        help="Starting page number (overrides config)"
    )
    
    parser.add_argument(
        "--end", 
        type=int,
        help="Ending page number (overrides config)"
    )
    
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume scraping (skip existing pages)"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true", 
        help="Show summary of scraped data and exit"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Configuration is in config.py (this option is deprecated)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    SHOOB.GG CARD SCRAPER                     ║
║                   Professional Edition v2.0                 ║
╠══════════════════════════════════════════════════════════════╣
║  Features:                                                   ║
║  • Live-save functionality (saves after each page)          ║
║  • Resume capability (skips already scraped pages)          ║
║  • Robust error handling and retry logic                    ║
║  • Comprehensive data extraction                             ║
║  • Anti-detection measures                                   ║
║  • Clean Windows output (no asyncio warnings)               ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(summary_data):
    """Print formatted data summary."""
    print("\n" + "="*60)
    print("📊 SCRAPED DATA SUMMARY")
    print("="*60)
    print(f"📁 Output file: {summary_data.get('output_file', 'N/A')}")
    print(f"🃏 Total cards: {summary_data.get('total_cards', 0)}")
    
    if summary_data.get('scraped_pages'):
        print(f"📋 Pages scraped: {sorted(summary_data['scraped_pages'])}")
        
    if summary_data.get('sample_cards'):
        print("\n🎴 Sample cards:")
        for card in summary_data['sample_cards'][:3]:
            print(f"   - {card['name']} (Tier {card['tier']}) from {card['series']}")
    
    if summary_data.get('file_size_mb'):
        print(f"📦 File size: {summary_data['file_size_mb']} MB")
    
    print("="*60)


async def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Setup Windows-specific fixes
    if sys.platform == "win32":
        suppress_asyncio_warnings()
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Print banner
    print_banner()
    
    try:
        # Initialize scraper
        print("🔧 Initializing scraper...")
        scraper = ShoobCardScraper()
        
        # Handle summary request
        if args.summary:
            print("📊 Generating data summary...")
            summary = scraper.get_scraped_data_summary()
            print_summary(summary)
            return
        
        # Configure verbose logging if requested
        if args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            print("🔍 Verbose logging enabled")
        
        # Determine scraping parameters
        start_page = args.start
        end_page = args.end
        
        if args.resume:
            print("🔄 Resume mode enabled - will skip existing pages")
        
        # Display scraping plan
        print(f"\n📋 Scraping Plan:")
        if start_page:
            print(f"   Start page: {start_page}")
        else:
            print(f"   Start page: {scraper.config['start_page']} (from config)")
            
        if end_page:
            print(f"   End page: {end_page}")
        else:
            end_config = scraper.config['end_page']
            if end_config:
                print(f"   End page: {end_config} (from config)")
            else:
                print(f"   End page: Auto-detect (will scrape until no more cards)")
        
        print(f"   Live-save: ✅ Enabled")
        print(f"   Data folder: {scraper.config['output_folder']}")
        
        # Confirm before starting
        if not args.resume:
            try:
                response = input("\n🚀 Ready to start scraping? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("❌ Scraping cancelled by user")
                    return
            except KeyboardInterrupt:
                print("\n❌ Scraping cancelled by user")
                return
        
        # Start scraping
        print("\n🚀 Starting scraping process...")
        print("-" * 60)
        
        stats = await scraper.scrape_all_pages(start_page, end_page)
        
        # Display final results
        print("\n" + "="*60)
        print("🎉 SCRAPING COMPLETED!")
        print("="*60)
        print(f"📄 Pages scraped: {stats['pages_scraped']}")
        print(f"📄 Pages skipped: {stats['pages_skipped']}")
        print(f"🃏 Cards extracted: {stats['cards_extracted']}")
        print(f"❌ Errors: {stats['errors']}")
        print(f"✅ Success rate: {stats['success_rate']}%")
        print(f"⏱️  Total time: {stats['elapsed_time']}s")
        print(f"🚀 Speed: {stats['cards_per_second']} cards/sec")
        print("="*60)
        
        # Show data summary
        if stats['cards_extracted'] > 0:
            print("\n📊 Getting final data summary...")
            summary = scraper.get_scraped_data_summary()
            print_summary(summary)
        
        print(f"\n💾 All data saved to: {scraper.config['output_folder']}")
        print("✨ Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrupted by user")
        print("💾 Any completed pages have been saved")
        print("🔄 Use --resume flag to continue from where you left off")
        
        # Ensure proper cleanup
        try:
            if 'scraper' in locals():
                await scraper._cleanup_browser()
        except:
            pass
        
    except FileNotFoundError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("💡 Make sure config.py exists in the same directory")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        print("💡 Check the logs for more details")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
    finally:
        # Force cleanup on Windows
        if sys.platform == "win32":
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    loop.close()
            except:
                pass
