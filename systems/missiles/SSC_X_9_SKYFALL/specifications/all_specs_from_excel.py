import re
import os
import pandas as pd 
from dataclasses import dataclass
from typing import Optional, List, Tuple
import json


@dataclass(frozen=True)
class AllSpecificationsFromExcel:
    stage_1_propulsion_type: Optional[str] = None
    stage_1_length: Optional[float] = None
    stage_1_diameter: Optional[float] = None
    stage_1_wet_mass: Optional[float] = None
    stage_1_dry_mass: Optional[float] = None
    stage_1_burn_time: Optional[float] = None
    stage_1_moment_of_inertia: Optional[float] = None

    separation_delay_after_stage_1_burnout: Optional[float] = None
    coating_time_between_stage_1_and_2: Optional[float] = None

    stage_2_propulsion_type: Optional[str] = None
    stage_2_length: Optional[float] = None
    stage_2_diameter: Optional[float] = None
    stage_2_wet_mass_per_booster: Optional[float] = None
    stage_2_dry_mass_per_booster: Optional[float] = None
    stage_2_burn_time: Optional[float] = None
    stage_2_moment_of_inertia: Optional[float] = None

    separation_delay_after_stage_2_burnout: Optional[float] = None
    coating_time_between_stage_2_and_3: Optional[float] = None

    stage_3_propulsion_type: Optional[str] = None
    stage_3_length: Optional[float] = None
    stage_3_height: Optional[float] = None
    stage_3_width: Optional[float] = None
    stage_3_mass: Optional[float] = None
    stage_3_moment_of_inertia: Optional[float] = None
    stage_3_centre_of_gravity_from_nose: Optional[float] = None
    stage_3_centre_of_pressure_from_nose: Optional[float] = None
    stage_3_wing_span: Optional[float] = None
    stage_3_tail_span: Optional[float] = None
    stage_3_wing_area: Optional[float] = None
    stage_3_tail_area: Optional[float] = None
    stage_3_distance_from_cog_to_wing_neutral_point: Optional[float] = None
    stage_3_distance_from_cog_to_tail_neutral_point: Optional[float] = None
    stage_3_wing_mean_aerodynamic_chord: Optional[float] = None
    stage_3_tail_mean_aerodynamic_chord: Optional[float] = None

    reactor_run_up_time: Optional[str] = None                # Changed to str since it's "A few minutes"
    variant_1_available_reactor_space: Optional[str] = None  # Changed to str since it contains ranges
    variant_2_available_reactor_space: Optional[str] = None  # Changed to str since it contains ranges

    full_length_with_booster: Optional[float] = None
    take_off_mass: Optional[float] = None
    warhead_mass: Optional[float] = None
    warhead_yield: Optional[float] = None
    centre_of_mass_from_nose_at_launch: Optional[float] = None

    cruise_velocity: Optional[float] = None
    launch_container_length: Optional[float] = None


def find_specifications_start(df):
    """Find the row index where 'Specifications' header is located"""
    for idx, row in df.iterrows():
        if not pd.isna(row.iloc[0]) and 'Specifications' in str(row.iloc[0]).strip():
            return idx
    return -1


def find_first_valid_value(row):
    """Find the first non-NaN value in a row starting from column 1"""
    for col_idx in range(1, len(row)):  # Start from column 1 (after the specification name)
        if not pd.isna(row.iloc[col_idx]):
            value = row.iloc[col_idx]
            # Clean numeric values
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, str):
                cleaned_value = value.strip()
                # Try to convert to number if it's purely numeric
                if cleaned_value.replace('.', '').replace('-', '').isdigit():
                    try:
                        num_value = float(cleaned_value)
                        return int(num_value) if num_value.is_integer() else num_value
                    except ValueError:
                        return cleaned_value
                return cleaned_value
            else:
                return value
    return None


def extract_specifications_data(excel_file_path, sheet_name='Specifications'):
    """
    Extract specifications data from Excel file by scanning all columns for values
    Args:
        excel_file_path (str): Path to the Excel file
        sheet_name (str): Name of the sheet to read
    Returns:
        dict: Dictionary with specification names as keys and their values
        list: Ordered list of (spec_name, value) tuples to maintain Excel order
    """
    try:
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=None)
        print("Excel sheet preview:")
        print(df.head(30))  # Show first 30 rows
        
        # Find where specifications start
        spec_start_row = find_specifications_start(df)
        if spec_start_row == -1:
            print("Warning: 'Specifications' header not found, using entire sheet")
            spec_start_row = 0
        else:
            spec_start_row += 1  # Start from row after 'Specifications'
            
        # Extract data starting from the specifications section
        specs_df = df.iloc[spec_start_row:].reset_index(drop=True)
        
        # Remove completely empty rows
        specs_df = specs_df.dropna(how='all').reset_index(drop=True)
        
        print(f"\nSpecifications section (starting from row {spec_start_row}):")
        print(specs_df)
        
        # Convert to dictionary format AND maintain order with list
        specifications_dict = {}
        ordered_specs_list = []  # List of (spec_name, value) tuples to preserve order
        
        for idx, row in specs_df.iterrows():
            if not pd.isna(row.iloc[0]):  # Check if first column (specification name) has data
                spec_name = str(row.iloc[0]).strip()
                # Find the first valid value across all columns (starting from column 1)
                value = find_first_valid_value(row)
                specifications_dict[spec_name] = value
                ordered_specs_list.append((spec_name, value))  # Preserve order
                
        return specifications_dict, ordered_specs_list, specs_df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return {}, [], pd.DataFrame()


def create_exact_field_mapping():
    """Create exact mapping between Excel column names and dataclass fields"""
    # Exact mapping based on your provided Excel column names
    mapping = {
        'Stage 1 propulsion type': 'stage_1_propulsion_type',
        'Stage 1 length [m]': 'stage_1_length',
        'Stage 1 diameter [m]': 'stage_1_diameter',
        'Stage 1 wet mass [kg]': 'stage_1_wet_mass',
        'Stage 1 dry mass [kg]': 'stage_1_dry_mass',
        'Stage 1 burn time [s]': 'stage_1_burn_time',
        'Stage 1 moment of inertia [kk]': 'stage_1_moment_of_inertia',
        
        'Separation delay after stage 1 burnout [s]': 'separation_delay_after_stage_1_burnout',
        'Coating time between stage 1 and 2 [s]': 'coating_time_between_stage_1_and_2',
        
        'Stage 2 propulsion type': 'stage_2_propulsion_type',
        'Stage 2 length [m]': 'stage_2_length',
        'Stage 2 diameter [m]': 'stage_2_diameter',
        'Stage 2 wet mass per booster [kg]': 'stage_2_wet_mass_per_booster',
        'Stage 2 dry mass per booster [kg]': 'stage_2_dry_mass_per_booster',
        'Stage 2 burn time [s]': 'stage_2_burn_time',
        'Stage 2 moment of inertia [kk]': 'stage_2_moment_of_inertia',
        
        'Separation delay after stage 2 burnout [s]': 'separation_delay_after_stage_2_burnout',
        'Coating time between stage 2 and 3 [s]': 'coating_time_between_stage_2_and_3',
        
        'Stage 3 propulsion type': 'stage_3_propulsion_type',
        'Stage 3 length [m]': 'stage_3_length',
        'Stage 3 height [m]': 'stage_3_height',
        'Stage 3 width [m]': 'stage_3_width',
        'Stage 3 mass [kg]': 'stage_3_mass',
        'Stage 3 moment of inertia [kk]': 'stage_3_moment_of_inertia',
        'Stage 3 centre of gravity from nose [m]': 'stage_3_centre_of_gravity_from_nose',
        'Stage 3 centre of pressure from nose [m]': 'stage_3_centre_of_pressure_from_nose',
        'Stage 3 wing span [m]': 'stage_3_wing_span',
        'Stage 3 tail span [m]': 'stage_3_tail_span',
        'Stage 3 wing area [m2]': 'stage_3_wing_area',
        'Stage 3 tail area [m2]': 'stage_3_tail_area',
        'Stage 3 distance from CoG to wing neutral point [m]': 'stage_3_distance_from_cog_to_wing_neutral_point',
        'Stage 3 distance from CoG to tail neutral point [m]': 'stage_3_distance_from_cog_to_tail_neutral_point',
        'Stage 3 wing mean aerodynamic cord [m]': 'stage_3_wing_mean_aerodynamic_chord',
        'Stage 3 tail mean aerodynamic cord [m]': 'stage_3_tail_mean_aerodynamic_chord',
        
        'Reactor run-up time': 'reactor_run_up_time',
        'Variant 1 available reactor space [dm3]': 'variant_1_available_reactor_space',
        'Variant 2 available reactor space [dm3]': 'variant_2_available_reactor_space',
        
        'Full length with booster [m]': 'full_length_with_booster',
        'Take-off mass [kg]': 'take_off_mass',
        'Warhead mass [kg]': 'warhead_mass',
        'Warhead yield [MT]': 'warhead_yield',
        'Centre of mass from nose at launch [m]': 'centre_of_mass_from_nose_at_launch',
        
        'Cruise velocity [m/s]': 'cruise_velocity',
        'Launch container length [m]': 'launch_container_length'
    }
    return mapping


def map_excel_to_dataclass(specs_dict, ordered_specs_list):
    """Map Excel specifications to dataclass fields using exact matching, maintaining order"""
    field_mapping = create_exact_field_mapping()
    
    # Initialize all fields with None
    mapped_values = {field: None for field in AllSpecificationsFromExcel.__dataclass_fields__.keys()}
    
    print("\n Mapping Excel keys to dataclass fields (in Excel order):")
    print("-" * 70)
    
    # Match Excel keys to dataclass fields in the order they appear in Excel
    matched_keys = set()
    for spec_name, spec_value in ordered_specs_list:
        if spec_name in field_mapping:
            field_name = field_mapping[spec_name]
            mapped_values[field_name] = spec_value
            print(f"'{spec_name}' -> {field_name} = {spec_value}")
            matched_keys.add(spec_name)
        else:
            print(f" Unmatched key: '{spec_name}' (value: {spec_value})")
    
    # Show mapping statistics
    total_excel_keys = len(specs_dict)
    matched_excel_keys = len(matched_keys)
    unmapped_excel_keys = total_excel_keys - matched_excel_keys
    
    print(f"\n Mapping Statistics:")
    print(f"   Total Excel specifications: {total_excel_keys}")
    print(f"   Successfully mapped: {matched_excel_keys}")
    print(f"   Unmapped: {unmapped_excel_keys}")
    print(f"   Success rate: {matched_excel_keys/total_excel_keys*100:.1f}%")
    
    # Show unmapped Excel keys (in original order)
    if unmapped_excel_keys > 0:
        unmapped_excel_keys_list = [spec_name for spec_name, _ in ordered_specs_list if spec_name not in matched_keys]
        print(f"\n Unmapped Excel keys (in order):")
        for key in unmapped_excel_keys_list:
            print(f"   '{key}'")
    
    # Show unmapped dataclass fields
    unmapped_fields = [field for field, value in mapped_values.items() if value is None]
    if unmapped_fields:
        print(f"\n Unmapped dataclass fields ({len(unmapped_fields)}):")
        for field in sorted(unmapped_fields):
            print(f"   {field}")
    
    return mapped_values


def populate_dataclass_from_excel(excel_file_path, sheet_name='Specifications'):
    """
    Populate the AllSpecificationsFromExcel dataclass from Excel data
    """
    specs_dict, ordered_specs_list, specs_df = extract_specifications_data(excel_file_path, sheet_name)
    
    if not specs_dict:
        print("No specifications data extracted")
        return None, {}, [], pd.DataFrame()
    
    try:
        # Map Excel data to dataclass fields
        mapped_values = map_excel_to_dataclass(specs_dict, ordered_specs_list)
        
        # Create dataclass instance
        specs_instance = AllSpecificationsFromExcel(**mapped_values)
        
        total_fields = len(mapped_values)
        mapped_fields = sum(1 for v in mapped_values.values() if v is not None)
        
        print(f"\n Successfully created dataclass instance!")
        print(f" Mapped {mapped_fields}/{total_fields} fields ({mapped_fields/total_fields*100:.1f}%)")
        
        return specs_instance, specs_dict, ordered_specs_list, specs_df
        
    except Exception as e:
        print(f" Error creating dataclass instance: {e}")
        import traceback
        traceback.print_exc()
        return None, specs_dict, ordered_specs_list, specs_df


specs_instance = None

# Main execution
if __name__ == "__main__":
    excel_file_path = r"U:\Documents\FGMØV\Lagt over på A6 mappen\WMD\Russia\SSC-X-9 SKYFALL\(HEB) SSC-X-9 SKYFALL.xlsx"    ############################# change SSC_X_9_SKYFALL_EXCEL_SHEET_FILEPATH
    
    print("Starting Excel specifications extraction...")
    print(f"Looking for Excel file at: {excel_file_path}")
    
    if os.path.exists(excel_file_path):
        print("Excel file found!")
        print(" ")
        
        # Extract specifications and populate dataclass
        specs_instance, specs_dict, ordered_specs_list, specs_df = populate_dataclass_from_excel(excel_file_path)
        
        # Display results in various formats
        print("\n" + "="*80)
        print("SPECIFICATIONS DATA PROCESSING RESULTS")
        print("="*80)
        
        # 1. Available specification keys from Excel (IN EXCEL ORDER)
        print(f"\n 1. Available specification keys from Excel ({len(specs_dict)} total) - IN EXCEL ORDER:")
        print("-" * 80)
        for spec_name, spec_value in ordered_specs_list:
            print(f"   '{spec_name}': {spec_value} ({type(spec_value).__name__})")
        
        # 2. Successfully mapped dataclass instance
        if specs_instance:
            print(f"\n 2. Successfully mapped dataclass instance (non-None values only):")
            print("-" * 80)
            # Show only non-None values in the order they appear in the dataclass
            mapped_count = 0
            for field_name, field_value in specs_instance.__dict__.items():
                if field_value is not None:
                    print(f"   {field_name}: {field_value}")
                    mapped_count += 1
            
            print(f"\n Summary: {mapped_count} fields successfully mapped out of {len(specs_instance.__dict__)}")
            
            # Show dataclass as dictionary for easy viewing
            print(f"\n 3. Complete dataclass content (non-None values only):")
            print("-" * 80)
            
            # Filter out None values for cleaner display
            non_none_values = {k: v for k, v in specs_instance.__dict__.items() if v is not None}
            print(json.dumps(non_none_values, indent=2, default=str))
        
        # 4. Raw DataFrame view
        print(f"\n 4. Raw DataFrame format (first 25 rows):")
        print("-" * 80)
        print(specs_df.head(25).to_string())
        
    else:
        print(f"Excel file not found at: {excel_file_path}")
        print("Please check the file path and name.")


all_specs_from_excel_instance = specs_instance