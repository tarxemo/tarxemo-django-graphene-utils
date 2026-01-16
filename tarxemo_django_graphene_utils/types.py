import graphene

class BaseType(graphene.ObjectType):
    """Base GraphQL type with common fields"""
    id = graphene.UUID()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    is_active = graphene.Boolean()

class LocationInput(graphene.InputObjectType):
    """Input type for location coordinates"""
    latitude = graphene.Float(required=True, description="Latitude in decimal degrees")
    longitude = graphene.Float(required=True, description="Longitude in decimal degrees")
    radius = graphene.Float(description="Search radius in kilometers")

class SeriesPoint(graphene.ObjectType):
    label = graphene.String()
    value = graphene.Float()
