from enum import Enum
from typing import List, Union


class OptionType(Enum):
    PUT = "PUT"
    CALL = "CALL"

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns a list containing the string values of the Enum members.
        """
        return sorted([member.value for member in cls])

    @classmethod
    def value_of(cls, value: Union[str, "OptionType"]) -> "OptionType":
        if isinstance(value, cls):
            return value
        elif isinstance(value, str):
            try:
                return cls(value.upper())
            except ValueError:
                raise ValueError(
                    f"'{value}' is not a valid OptionType value. Must be 'PUT' or 'CALL'."
                )
        else:
            raise TypeError(
                f"Invalid type for value: {type(value)}. Expected str or OptionType."
            )
