"""
Deduplication Step - Removes duplicate vehicle listings

This step implements the modular separation strategy for data deduplication with
high-quality standardized process output and exceptional maintainability.

PROVIDES: Deduplication of vehicle listings based on multiple criteria
DEPENDS: Transformation step
CONSUMED BY: Fair value calculation step
CONTRACT: Provides unique vehicle listings
TECH CHOICE: Modular deduplication with clear separation of concerns
RISK: Low - deduplication logic is straightforward
"""

import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BasePipelineStep, StepResult


class DeduplicationStep(BasePipelineStep):
    """Deduplication step implementing modular separation strategy"""
    
    def get_step_name(self) -> str:
        return "deduplication"
    
    def get_description(self) -> str:
        return "Removes duplicate vehicle listings based on VIN and other criteria"
    
    def get_dependencies(self) -> List[str]:
        return ["transformation"]  # Depends on transformation step
    
    def get_required_config(self) -> List[str]:
        return ["pipeline"]  # Needs pipeline configuration
    
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the deduplication step with high-quality process output"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            print("🔄 Starting deduplication process...")
            print(f"📁 Working directory: {Path.cwd()}")
            print(f"⏰ Deduplication started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Get transformation results
            if "transformation" in previous_results:
                transform_result = previous_results["transformation"]
                if not transform_result.is_success:
                    print("❌ Transformation step must complete successfully before deduplication")
                    raise ValueError("Transformation step must complete successfully before deduplication")

                transformed_data = transform_result.data.get("transformed_data", [])
            else:
                # Single step execution - no mock data allowed
                print("❌ No transformation results found - transformation step must run first")
                raise ValueError("Transformation step must complete successfully before deduplication")

            if not transformed_data:
                print("⚠️  No data to deduplicate")
                return {
                    "original_count": 0,
                    "final_count": 0,
                    "duplicates_removed": 0,
                    "deduped_data": [],
                    "deduplication_stats": {
                        "duplicate_rate": 0,
                        "retention_rate": 0
                    },
                    "deduplication_timestamp": datetime.now().isoformat()
                }

            print(f"📊 Processing {len(transformed_data)} transformed listings...")

            # Step 1: Analyze data structure
            print("🔍 Step 1: Analyzing data structure...")
            data_structure = self._analyze_data_structure(transformed_data)

            # Step 2: Identify duplicate detection criteria
            print("🔍 Step 2: Identifying duplicate detection criteria...")
            duplicate_criteria = self._identify_duplicate_criteria(data_structure)

            # Step 3: Perform deduplication
            print("🔄 Step 3: Performing deduplication...")
            deduped_data = self._perform_deduplication(transformed_data, duplicate_criteria)

            # Step 4: Save deduplication results
            print("📄 Step 4: Saving deduplication results...")
            saved_files = self._save_deduplication_results(transformed_data, deduped_data, config)

            # Step 5: Generate deduplication summary
            print("📊 Step 5: Generating deduplication summary...")
            deduplication_summary = self._generate_deduplication_summary(
                transformed_data, deduped_data, saved_files
            )

            print("✅ Deduplication completed successfully!")
            print(f"📊 Processed {len(transformed_data)} original listings")
            print(f"✅ Retained {len(deduped_data)} unique listings")
            print(f"🗑️  Removed {len(transformed_data) - len(deduped_data)} duplicates")
            print(f"📄 Saved results to {len(saved_files)} files")

            return deduplication_summary
        finally:
            builtins.print = _orig_print
    
    def _analyze_data_structure(self, transformed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the structure of transformed data to understand available fields"""
        print("     🔍 Analyzing data fields and types...")
        
        if not transformed_data:
            return {}
        
        # Get all unique field names
        all_fields = set()
        for item in transformed_data:
            all_fields.update(item.keys())
        
        # Analyze field types and values
        field_analysis = {}
        for field in sorted(all_fields):
            values = [item.get(field) for item in transformed_data if item.get(field) is not None]
            field_analysis[field] = {
                'count': len(values),
                'unique_count': len(set(values)),
                'sample_values': values[:3] if values else [],
                'has_duplicates': len(values) > len(set(values)) if values else False
            }
        
        print(f"       📋 Found {len(all_fields)} fields in transformed data")
        print(f"       🔍 Fields with potential duplicates: {[f for f, a in field_analysis.items() if a['has_duplicates']]}")
        
        return field_analysis
    
    def _identify_duplicate_criteria(self, data_structure: Dict[str, Any]) -> List[str]:
        """Identify the best criteria for detecting duplicates"""
        print("     🔍 Identifying duplicate detection criteria...")
        
        # Priority order for duplicate detection
        priority_criteria = [
            'vin',            # VIN is the most reliable identifier
            'listing_url',    # URL should be unique
            'source_url',     # Source + other fields
            'year',           # Year + model + mileage combination
            'model',          # Prefer separate fields
            'trim',           # Prefer separate fields
            'model_trim'      # Legacy combined field (fallback)
        ]
        
        # Find available criteria from priority list
        available_criteria = []
        for criterion in priority_criteria:
            if criterion in data_structure:
                available_criteria.append(criterion)
                print(f"       ✅ Using criterion: {criterion}")
        
        if not available_criteria:
            # Fallback to any field that might have duplicates
            available_criteria = [field for field, analysis in data_structure.items() 
                               if analysis['has_duplicates']]
            print(f"       ⚠️  Using fallback criteria: {available_criteria}")
        
        return available_criteria
    
    def _perform_deduplication(self, transformed_data: List[Dict[str, Any]], 
                              duplicate_criteria: List[str]) -> List[Dict[str, Any]]:
        """Perform deduplication based on identified criteria"""
        print("     🔄 Performing deduplication...")
        
        if not duplicate_criteria:
            print("       ⚠️  No duplicate criteria identified, returning original data")
            return transformed_data
        
        # Create composite keys for deduplication
        seen_keys = set()
        deduped_data = []
        duplicates_found = []
        
        for item in transformed_data:
            # Create composite key from criteria
            composite_key = self._create_composite_key(item, duplicate_criteria)
            
            if composite_key in seen_keys:
                duplicates_found.append(item)
                print(f"       🗑️  Duplicate found: {composite_key}")
            else:
                seen_keys.add(composite_key)
                deduped_data.append(item)
        
        print(f"       ✅ Deduplication complete: {len(transformed_data)} → {len(deduped_data)} listings")
        print(f"       🗑️  Removed {len(duplicates_found)} duplicates")
        
        return deduped_data
    
    def _create_composite_key(self, item: Dict[str, Any], criteria: List[str]) -> str:
        """Create a composite key from the specified criteria"""
        key_parts = []
        for criterion in criteria:
            value = item.get(criterion, '')
            if value:
                key_parts.append(f"{criterion}:{value}")
        
        return "|".join(sorted(key_parts)) if key_parts else "unknown"
    
    def _save_deduplication_results(self, original_data: List[Dict[str, Any]], 
                                  deduped_data: List[Dict[str, Any]], 
                                  config: Dict[str, Any]) -> List[str]:
        """Save deduplication results to files"""
        print("     📄 Saving deduplication results...")
        
        output_dir = Path(config.get('pipeline', {}).get('output_directory', 'x987-data/results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        # Save deduplicated data
        deduped_filename = f"deduplicated_data_{timestamp}.csv"
        deduped_filepath = output_dir / deduped_filename
        
        try:
            with open(deduped_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if deduped_data:
                    fieldnames = deduped_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in deduped_data:
                        writer.writerow(row)
            
            saved_files.append(str(deduped_filepath))
            print(f"       ✅ Created {deduped_filename} with {len(deduped_data)} rows")
            
        except Exception as e:
            print(f"       ❌ Error creating {deduped_filename}: {e}")
        
        # Save deduplication summary
        summary_filename = f"deduplication_summary_{timestamp}.csv"
        summary_filepath = output_dir / summary_filename
        
        try:
            with open(summary_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['metric', 'value', 'timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                summary_data = [
                    {'metric': 'original_count', 'value': len(original_data), 'timestamp': timestamp},
                    {'metric': 'final_count', 'value': len(deduped_data), 'timestamp': timestamp},
                    {'metric': 'duplicates_removed', 'value': len(original_data) - len(deduped_data), 'timestamp': timestamp},
                    {'metric': 'duplicate_rate', 'value': (len(original_data) - len(deduped_data)) / len(original_data) if original_data else 0, 'timestamp': timestamp},
                    {'metric': 'retention_rate', 'value': len(deduped_data) / len(original_data) if original_data else 0, 'timestamp': timestamp}
                ]
                
                for row in summary_data:
                    writer.writerow(row)
            
            saved_files.append(str(summary_filepath))
            print(f"       ✅ Created {summary_filename}")
            
        except Exception as e:
            print(f"       ❌ Error creating {summary_filename}: {e}")
        
        return saved_files
    
    def _generate_deduplication_summary(self, original_data: List[Dict[str, Any]], 
                                     deduped_data: List[Dict[str, Any]], 
                                     saved_files: List[str]) -> Dict[str, Any]:
        """Generate comprehensive deduplication summary"""
        
        # Calculate statistics
        original_count = len(original_data)
        final_count = len(deduped_data)
        duplicates_removed = original_count - final_count
        
        summary = {
            "original_count": original_count,
            "final_count": final_count,
            "duplicates_removed": duplicates_removed,
            "deduped_data": deduped_data,
            "saved_files": saved_files,
            "deduplication_stats": {
                "duplicate_rate": duplicates_removed / original_count if original_count > 0 else 0,
                "retention_rate": final_count / original_count if original_count > 0 else 0,
                "efficiency": duplicates_removed / original_count if original_count > 0 else 0
            },
            "deduplication_timestamp": datetime.now().isoformat()
        }
        
        return summary


# Export the deduplication step instance
DEDUPLICATION_STEP = DeduplicationStep()
