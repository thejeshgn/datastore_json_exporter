from django.contrib.gis import gdal
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class SpatialRefSysMixin(object):
    """
    The SpatialRefSysMixin is a class used by the database-dependent
    SpatialRefSys objects to reduce redundant code.
    """
    @property
    def srs(self):
        """
        Returns a GDAL SpatialReference object.
        """
        # TODO: Is caching really necessary here?  Is complexity worth it?
        if hasattr(self, '_srs'):
            # Returning a clone of the cached SpatialReference object.
            return self._srs.clone()
        else:
            # Attempting to cache a SpatialReference object.

            # Trying to get from WKT first.
            try:
                self._srs = gdal.SpatialReference(self.wkt)
                return self.srs
            except Exception as e:
                msg = e

            try:
                self._srs = gdal.SpatialReference(self.proj4text)
                return self.srs
            except Exception as e:
                msg = e

            raise Exception('Could not get OSR SpatialReference from WKT: %s\nError:\n%s' % (self.wkt, msg))

    @property
    def ellipsoid(self):
        """
        Returns a tuple of the ellipsoid parameters:
        (semimajor axis, semiminor axis, and inverse flattening).
        """
        return self.srs.ellipsoid

    @property
    def name(self):
        "Returns the projection name."
        return self.srs.name

    @property
    def spheroid(self):
        "Returns the spheroid name for this spatial reference."
        return self.srs['spheroid']

    @property
    def datum(self):
        "Returns the datum for this spatial reference."
        return self.srs['datum']

    @property
    def projected(self):
        "Is this Spatial Reference projected?"
        return self.srs.projected

    @property
    def local(self):
        "Is this Spatial Reference local?"
        return self.srs.local

    @property
    def geographic(self):
        "Is this Spatial Reference geographic?"
        return self.srs.geographic

    @property
    def linear_name(self):
        "Returns the linear units name."
        return self.srs.linear_name

    @property
    def linear_units(self):
        "Returns the linear units."
        return self.srs.linear_units

    @property
    def angular_name(self):
        "Returns the name of the angular units."
        return self.srs.angular_name

    @property
    def angular_units(self):
        "Returns the angular units."
        return self.srs.angular_units

    @property
    def units(self):
        "Returns a tuple of the units and the name."
        if self.projected or self.local:
            return (self.linear_units, self.linear_name)
        elif self.geographic:
            return (self.angular_units, self.angular_name)
        else:
            return (None, None)

    @classmethod
    def get_units(cls, wkt):
        """
        Return a tuple of (unit_value, unit_name) for the given WKT without
        using any of the database fields.
        """
        return gdal.SpatialReference(wkt).units

    @classmethod
    def get_spheroid(cls, wkt, string=True):
        """
        Class method used by GeometryField on initialization to
        retrieve the `SPHEROID[..]` parameters from the given WKT.
        """
        srs = gdal.SpatialReference(wkt)
        sphere_params = srs.ellipsoid
        sphere_name = srs['spheroid']

        if not string:
            return sphere_name, sphere_params
        else:
            # `string` parameter used to place in format acceptable by PostGIS
            if len(sphere_params) == 3:
                radius, flattening = sphere_params[0], sphere_params[2]
            else:
                radius, flattening = sphere_params
            return 'SPHEROID["%s",%s,%s]' % (sphere_name, radius, flattening)

    def __str__(self):
        """
        Returns the string representation, a 'pretty' OGC WKT.
        """
        return six.text_type(self.srs)
