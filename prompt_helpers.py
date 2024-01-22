
def building_height_description(num_stories):
    num_stories = int(num_stories)
    if num_stories <= 5:
        return "a very-low"
    elif num_stories <= 10:
        return "a taller low-rise"
    elif num_stories <= 20:
        return "a mid-rise"
    elif num_stories <= 30:
        return "a taller mid-rise"
    elif num_stories <= 40:
        return "a small high-rise"
    elif num_stories <= 50:
        return "a medium high-rise"
    elif num_stories <= 60:
        return "a small skyscraper"
    elif num_stories <= 70:
        return "a medium skyscraper"
    elif num_stories <= 80:
        return "a large skyscraper"
    elif num_stories <= 90:
        return "a very large skyscraper"
    else:  # 91 to 100 stories
        return "a landmark ultra-tall skyscraper"
    

def make_image_prompt(building_type, num_stories, color_finishes, primary_materials, location_context, landscape_type, architectural_style, quality_tier, additional_elements, qualitative_height):
    # Define the template for the building description
    template = (
        "You are a building visualizer. Your task is to generate an image with the following description with extreme accuracy."
        "The building type is: {building_type}. "
        "The building height is: {qualitative_height}, with {num_stories} stories. "
        "The building location context is (This describes the building's surroundings): {location_context}. "
        "The landscape type is: {landscape_type}. "
        "The building design quality is: {quality_tier}, where the available options are standard, premium and luxury. "
        "The architectural style is: {architectural_style}. "
        "The building facade is: {color_finishes}. "
        "The building materials are mostly: {primary_materials}. "
        "Here are some additional elements to add to the building: {additional_elements}. "
        "DO NOT WRITE TEXT ON THE IMAGE. "
        "Make the model high quality and high resolution. "
        "The view is from a higher angle than the building, so we can see the roof top, but also the facade and the street. "
        "The sky is blue, like a sunny and colorful day."
    )
    # Fill in the placeholders in the template with the form values
    prompt = template.format(
        num_stories=num_stories,
        building_type=building_type,
        color_finishes=color_finishes,
        location_context=location_context,
        landscape_type=landscape_type,
        architectural_style=architectural_style,
        quality_tier=quality_tier,
        primary_materials=primary_materials,
        additional_elements=additional_elements,
        qualitative_height=qualitative_height,
    )
    # Return the prompt
    return prompt

