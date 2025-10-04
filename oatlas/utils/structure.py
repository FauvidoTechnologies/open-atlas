from pydantic import BaseModel


class VertexaiGeolocationResponse(BaseModel):
    """
    The ImageGeolocation response is delibrate enough to force it to look at
    all the possible scenrios before evaluation
    """

    Initial_observations: str
    Geographical_clues: str
    Cultural_structural_clues: str
    reasoning: str
    final_estimate: str


class VertexaiTextExtractResponse(BaseModel):
    """
    This will be changed soon...
    """

    text_in_image: str
    image_description: str
