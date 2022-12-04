"""Config flow to configure PowerDog component."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult, FlowHandler
import homeassistant.helpers.config_validation as cv

from powerdog import powerdog_api
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class PowerdogConfigFlow(FlowHandler, domain=DOMAIN):
    """Handle a config flow for PowerDog."""

    VERSION = 1

    async def async_step_user(
        self, user_input = None
    ) -> FlowResult:
        """User step in config flow."""
        data_schema = {
            vol.Required("username"): str,
            vol.Required("password"): str,
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=errors
        )
        # errors = {}
        # if user_input is not None:
        #     try:
        #         apikey = powerdog_api.get_apikey(
        #             user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
        #         )
        #     except powerdog_api.APICallResultInvalidException:
        #         errors["base"] = "cannot_connect"
        #     except powerdog_api.NoItemFoundException:
        #         errors["base"] = "cannot_retrieve_device_info"

        #     if not errors:
        #         await self.async_set_unique_id(
        #             powerdog_api.get_powerdog_uids(apikey)[0]
        #         )
        #         self._abort_if_unique_id_configured()
        #     return self.async_create_entry(
        #         title=user_input[CONF_EMAIL], data=user_input
        #     )

        # return self.async_show_form(
        #     step_id="user",
        #     data_schema=vol.Schema(
        #         {
        #             vol.Required(CONF_EMAIL): cv.string,
        #             vol.Required(CONF_PASSWORD): cv.string,
        #         }
        #     ),
        #     errors=errors,
        # )
