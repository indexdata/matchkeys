# Matcher - goldrush2021

This implements the "Gold Rush - Colorado Alliance MARC record match key generation" (specification dated September 2021).

## Status

Each component of the specification is implemented.

We use it in production at all consortia.

## Components

Each component of the matchkey is padded with the underscore character to fill to its field width.

## Configuration

> [!IMPORTANT]
> Note that the example configuration refers to its JavaScript implementation via a specific git commit SHA (and might not be current).
> Operators should manage their own configuration files and not use these examples directly.
