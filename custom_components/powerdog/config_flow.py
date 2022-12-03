"""Config flow to configure PowerDog component."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from powerdog import powerdog_api
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class PowerdogConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PowerDog."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._data = {
            CONF_EMAIL: vol.UNDEFINED,
            CONF_PASSWORD: vol.UNDEFINED,
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step in config flow."""
        errors = {}
        if user_input is not None:
            try:
                apikey = powerdog_api.get_apikey(
                    user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
                )
            except powerdog_api.APICallResultInvalidException:
                errors["base"] = "cannot_connect"
            except powerdog_api.NoItemFoundException:
                errors["base"] = "cannot_retrieve_device_info"

            if not errors:
                await self.async_set_unique_id(
                    powerdog_api.get_powerdog_uids(apikey)[0]
                )
                self._abort_if_unique_id_configured(updates=self._data)
            return self.async_create_entry(
                title=self._data[CONF_EMAIL], data=self._data
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                }
            ),
            errors=errors,
        )
