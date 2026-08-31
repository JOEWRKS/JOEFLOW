"""Deterministic local runtime fixture for the bounded Client Feedback Portal dogfood.

The fixture implements the six approved dogfood actions against mutable local
state.  It has no network, clock, host-path, or Product Definition dependency;
the compiled 2.1 contract supplies the approved actor values used at runtime.
"""

from __future__ import annotations

import copy
import json


FIXTURE_PROJECT_ID = "project-fixture-001"
FIXTURE_VERSION_ID = "version-fixture-001"
FIXTURE_REVIEWER_EMAIL = "client-reviewer@example.test"

_ACTION_IDS = {
    "create_pin",
    "reply_thread",
    "resolve_thread",
    "send_review_request",
    "resend_review_request",
    "revoke_review_link",
}
_REVIEW_ACTIONS = {
    "send_review_request",
    "resend_review_request",
    "revoke_review_link",
}
_MESSAGE_ACTIONS = {"create_pin", "reply_thread", "resolve_thread"}


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _number(value: object) -> bool:
    return type(value) in {int, float}


class ClientFeedbackPortalFixture:
    """Execute approved portal actions and capture frozen-transport snapshots."""

    def __init__(
        self,
        contract: dict[str, object],
        *,
        initial_version_status: str = "DRAFT",
    ) -> None:
        if contract.get("contract_schema_version") != "joewrks.action-conformance/2.1":
            raise ValueError("INVALID_ACTION_CONTRACT_V21")
        actions = contract.get("actions")
        if not isinstance(actions, list):
            raise ValueError("INVALID_ACTION_CONTRACT_V21")
        action_index = {
            action.get("action_id"): action
            for action in actions
            if isinstance(action, dict)
        }
        if set(action_index) != _ACTION_IDS:
            raise ValueError("UNSUPPORTED_DOGFOOD_ACTION_INVENTORY")
        self._actors = {
            action_id: copy.deepcopy(action["fields"]["actor"]["value"])
            for action_id, action in action_index.items()
        }
        if initial_version_status not in {"DRAFT", "IN_REVIEW", "APPROVED"}:
            raise ValueError("INVALID_FIXTURE_VERSION_STATUS")
        self._authoritative_state: dict[str, object] = {
            "project_id": FIXTURE_PROJECT_ID,
            "version": {
                "version_id": FIXTURE_VERSION_ID,
                "status": initial_version_status,
                "revision": 1,
            },
            "review_link_revision": 0,
            "active_review_link_id": None,
            "review_links": [],
            "pins": [],
            "threads": [],
        }
        self._revision = 1
        self._history: list[dict[str, object]] = []
        self._business_effects: list[dict[str, object]] = []
        self._delivery_effects: list[dict[str, object]] = []
        self._attempt_results: dict[str, dict[str, object]] = {}
        self._next_pin = 1
        self._next_reply = 1
        self._next_link = 1

    def snapshot(self) -> dict[str, object]:
        return copy.deepcopy({
            "authoritative_state": self._authoritative_state,
            "revision": self._revision,
            "history": self._history,
            "business_side_effects": self._business_effects,
            "delivery_effects": self._delivery_effects,
        })

    def execute(self, command: dict[str, object]) -> dict[str, object]:
        if not isinstance(command, dict):
            raise TypeError("fixture command must be an object")
        command = copy.deepcopy(command)
        before = self.snapshot()
        action_id = command.get("action_id")
        if action_id == "create_pin":
            result = self._create_pin(command)
        elif action_id == "reply_thread":
            result = self._reply_thread(command)
        elif action_id == "resolve_thread":
            result = self._resolve_thread(command)
        elif action_id in _REVIEW_ACTIONS:
            result = self._review_link_action(command)
        else:
            result = self._rejected("UNKNOWN_ACTION")
        after = self.snapshot()
        return {
            "command": command,
            "before": before,
            "result": copy.deepcopy(result),
            "after": after,
            "deltas": self._deltas(before, after),
        }

    @staticmethod
    def _deltas(
        before: dict[str, object],
        after: dict[str, object],
    ) -> dict[str, object]:
        authoritative_delta = {
            key: copy.deepcopy(value)
            for key, value in after["authoritative_state"].items()
            if before["authoritative_state"].get(key) != value
        }
        return {
            "authoritative_state": authoritative_delta,
            "revision": after["revision"] - before["revision"],
            "history": copy.deepcopy(after["history"][len(before["history"]):]),
            "business_side_effects": copy.deepcopy(
                after["business_side_effects"][len(before["business_side_effects"]):]
            ),
            "delivery_effects": copy.deepcopy(
                after["delivery_effects"][len(before["delivery_effects"]):]
            ),
        }

    def _allowed_actor(self, action_id: str, actor: object) -> bool:
        approved = self._actors[action_id]
        return actor in approved if isinstance(approved, list) else actor == approved

    @staticmethod
    def _rejected(code: str) -> dict[str, object]:
        return {"result_class": "REJECTED", "error": {"code": code}}

    def _context_valid(self, command: dict[str, object]) -> bool:
        return (
            command.get("project_id") == FIXTURE_PROJECT_ID
            and command.get("version_id") == FIXTURE_VERSION_ID
        )

    def _version_status(self) -> str:
        return self._authoritative_state["version"]["status"]

    def _state_revision_guard(
        self,
        command: dict[str, object],
    ) -> dict[str, object] | None:
        expected = command.get("expected_state_revision")
        if type(expected) is not int or expected < 0:
            return self._rejected("EXPECTED_STATE_REVISION_REQUIRED")
        version = self._authoritative_state["version"]
        if expected != version["revision"]:
            return {
                "result_class": "STALE",
                "latest_state_revision": version["revision"],
                "latest_version": copy.deepcopy(version),
            }
        return None

    def _attempt_key(self, action_id: str, command: dict[str, object]) -> tuple[str, object]:
        field = "client_attempt_id" if action_id in _REVIEW_ACTIONS else "message_attempt_id"
        namespace = "review" if action_id in _REVIEW_ACTIONS else "message"
        return f"{namespace}:{command.get(field)}", command.get(field)

    def _prior_attempt(
        self,
        action_id: str,
        command: dict[str, object],
    ) -> dict[str, object] | None:
        key, attempt_id = self._attempt_key(action_id, command)
        if not _nonblank(attempt_id):
            return None
        previous = self._attempt_results.get(key)
        if previous is None:
            return None
        if previous["fingerprint"] != _canonical(command):
            return self._rejected("ATTEMPT_ID_CONFLICT")
        result = copy.deepcopy(previous["result"])
        if result.get("result_class") == "SUCCESS":
            return {
                "result_class": "IDEMPOTENT_REPLAY",
                "committed_result": result,
            }
        return result

    def _remember_attempt(
        self,
        action_id: str,
        command: dict[str, object],
        result: dict[str, object],
    ) -> None:
        key, attempt_id = self._attempt_key(action_id, command)
        if not _nonblank(attempt_id):
            return
        self._attempt_results[key] = {
            "fingerprint": _canonical(command),
            "result": copy.deepcopy(result),
        }

    def _commit(
        self,
        *,
        action_id: str,
        actor: str,
        history: dict[str, object],
        business_effect: dict[str, object],
        delivery_effect: dict[str, object] | None = None,
    ) -> None:
        self._revision += 1
        self._authoritative_state["version"]["revision"] += 1
        sequence = len(self._history) + 1
        self._history.append({
            "sequence": sequence,
            "action_id": action_id,
            "actor": actor,
            **copy.deepcopy(history),
        })
        self._business_effects.append({
            "sequence": len(self._business_effects) + 1,
            "action_id": action_id,
            **copy.deepcopy(business_effect),
        })
        if delivery_effect is not None:
            self._delivery_effects.append({
                "sequence": len(self._delivery_effects) + 1,
                "action_id": action_id,
                **copy.deepcopy(delivery_effect),
            })

    def _create_pin(self, command: dict[str, object]) -> dict[str, object]:
        replay = self._prior_attempt("create_pin", command)
        if replay is not None:
            return replay
        if not _nonblank(command.get("message_attempt_id")):
            return self._rejected("MESSAGE_ATTEMPT_ID_REQUIRED")
        if not self._allowed_actor("create_pin", command.get("actor")):
            return self._rejected("ACTOR_NOT_ALLOWED")
        if not self._context_valid(command):
            return self._rejected("OBJECT_BINDING_MISMATCH")
        revision_result = self._state_revision_guard(command)
        if revision_result is not None:
            return revision_result
        if self._version_status() == "APPROVED":
            return self._rejected("VERSION_READ_ONLY")
        media_type = command.get("media_type")
        coordinates_valid = (
            _number(command.get("x"))
            and _number(command.get("y"))
            and 0 <= command["x"] <= 1
            and 0 <= command["y"] <= 1
        )
        page_valid = media_type != "PDF" or (
            type(command.get("page")) is int and command["page"] >= 1
        )
        if (
            media_type not in {"IMAGE", "PDF"}
            or not coordinates_valid
            or not page_valid
            or not _nonblank(command.get("comment"))
        ):
            return self._rejected("PIN_INPUT_INVALID")
        pin_id = f"pin-{self._next_pin:03d}"
        thread_id = f"thread-{self._next_pin:03d}"
        self._next_pin += 1
        pin = {
            "pin_id": pin_id,
            "thread_id": thread_id,
            "version_id": FIXTURE_VERSION_ID,
            "media_type": media_type,
            "x": command["x"],
            "y": command["y"],
            "root_comment": command["comment"],
        }
        if media_type == "PDF":
            pin["page"] = command["page"]
        thread = {
            "thread_id": thread_id,
            "pin_id": pin_id,
            "status": "OPEN",
            "root_comment": command["comment"],
            "replies": [],
        }
        self._authoritative_state["pins"].append(pin)
        self._authoritative_state["threads"].append(thread)
        self._commit(
            action_id="create_pin",
            actor=command["actor"],
            history={"event": "PIN_CREATED", "pin_id": pin_id, "thread_id": thread_id},
            business_effect={"effect": "PIN_CREATED", "pin_id": pin_id, "thread_id": thread_id},
        )
        result = {
            "result_class": "SUCCESS",
            "pin_id": pin_id,
            "thread_id": thread_id,
            "version_id": FIXTURE_VERSION_ID,
        }
        self._remember_attempt("create_pin", command, result)
        return result

    def _thread(self, thread_id: object) -> dict[str, object] | None:
        return next(
            (
                thread
                for thread in self._authoritative_state["threads"]
                if thread["thread_id"] == thread_id
            ),
            None,
        )

    def _reply_thread(self, command: dict[str, object]) -> dict[str, object]:
        replay = self._prior_attempt("reply_thread", command)
        if replay is not None:
            return replay
        if not _nonblank(command.get("message_attempt_id")):
            return self._rejected("MESSAGE_ATTEMPT_ID_REQUIRED")
        if not self._allowed_actor("reply_thread", command.get("actor")):
            return self._rejected("ACTOR_NOT_ALLOWED")
        if not self._context_valid(command):
            return self._rejected("OBJECT_BINDING_MISMATCH")
        revision_result = self._state_revision_guard(command)
        if revision_result is not None:
            return revision_result
        if self._version_status() == "APPROVED":
            return self._rejected("VERSION_READ_ONLY")
        thread = self._thread(command.get("thread_id"))
        if thread is None:
            return self._rejected("THREAD_NOT_FOUND")
        if not _nonblank(command.get("message")):
            return self._rejected("REPLY_INPUT_INVALID")
        reply_id = f"reply-{self._next_reply:03d}"
        self._next_reply += 1
        reply = {
            "reply_id": reply_id,
            "actor": command["actor"],
            "message": command["message"],
        }
        thread["replies"].append(reply)
        reopened = thread["status"] == "RESOLVED" and command["actor"] == "Client Reviewer"
        if reopened:
            thread["status"] = "OPEN"
        self._commit(
            action_id="reply_thread",
            actor=command["actor"],
            history={
                "event": "THREAD_REPLY_APPENDED",
                "thread_id": thread["thread_id"],
                "reply_id": reply_id,
                "reopened": reopened,
            },
            business_effect={
                "effect": "THREAD_REPLY_APPENDED",
                "thread_id": thread["thread_id"],
                "reply_id": reply_id,
            },
        )
        result = {
            "result_class": "SUCCESS",
            "thread_id": thread["thread_id"],
            "reply_id": reply_id,
            "thread_status": thread["status"],
            "self_confirmation_email_sent": False,
        }
        self._remember_attempt("reply_thread", command, result)
        return result

    def _resolve_thread(self, command: dict[str, object]) -> dict[str, object]:
        replay = self._prior_attempt("resolve_thread", command)
        if replay is not None:
            return replay
        if not _nonblank(command.get("message_attempt_id")):
            return self._rejected("MESSAGE_ATTEMPT_ID_REQUIRED")
        if not self._allowed_actor("resolve_thread", command.get("actor")):
            return self._rejected("ACTOR_NOT_ALLOWED")
        if not self._context_valid(command):
            return self._rejected("OBJECT_BINDING_MISMATCH")
        revision_result = self._state_revision_guard(command)
        if revision_result is not None:
            return revision_result
        if self._version_status() == "APPROVED":
            return self._rejected("VERSION_READ_ONLY")
        thread = self._thread(command.get("thread_id"))
        if thread is None:
            return self._rejected("THREAD_NOT_FOUND")
        if thread["status"] != "OPEN":
            return self._rejected("THREAD_NOT_OPEN")
        thread["status"] = "RESOLVED"
        self._commit(
            action_id="resolve_thread",
            actor=command["actor"],
            history={"event": "THREAD_RESOLVED", "thread_id": thread["thread_id"]},
            business_effect={"effect": "THREAD_RESOLVED", "thread_id": thread["thread_id"]},
        )
        result = {
            "result_class": "SUCCESS",
            "thread_id": thread["thread_id"],
            "thread_status": "RESOLVED",
            "notification_sent": False,
        }
        self._remember_attempt("resolve_thread", command, result)
        return result

    def _active_link(self) -> dict[str, object] | None:
        active_id = self._authoritative_state["active_review_link_id"]
        return next(
            (
                link
                for link in self._authoritative_state["review_links"]
                if link["link_id"] == active_id
            ),
            None,
        )

    def _latest_review_link_result(self) -> dict[str, object]:
        return {
            "latest_review_link_revision": self._authoritative_state["review_link_revision"],
            "latest_review_link": copy.deepcopy(self._active_link()),
        }

    def _review_link_action(self, command: dict[str, object]) -> dict[str, object]:
        action_id = command["action_id"]
        replay = self._prior_attempt(action_id, command)
        if replay is not None:
            return replay
        if (
            not _nonblank(command.get("client_attempt_id"))
            or type(command.get("expected_review_link_revision")) is not int
            or command["expected_review_link_revision"] < 0
        ):
            return self._rejected("REVIEW_ATTEMPT_INPUT_REQUIRED")
        if not self._allowed_actor(action_id, command.get("actor")):
            return self._rejected("ACTOR_NOT_ALLOWED")
        if not self._context_valid(command):
            return self._rejected("OBJECT_BINDING_MISMATCH")
        if command.get("recipient") != FIXTURE_REVIEWER_EMAIL:
            return self._rejected("REVIEW_RECIPIENT_MISMATCH")
        expected_revision = command["expected_review_link_revision"]
        if expected_revision != self._authoritative_state["review_link_revision"]:
            result = {"result_class": "STALE", **self._latest_review_link_result()}
            self._remember_attempt(action_id, command, result)
            return result
        active = self._active_link()
        if action_id == "send_review_request" and self._version_status() != "DRAFT":
            return self._rejected("VERSION_STATE_INVALID")
        if action_id == "resend_review_request" and (
            self._version_status() != "IN_REVIEW" or active is None
        ):
            return self._rejected("ACTIVE_REVIEW_LINK_REQUIRED")
        if action_id == "revoke_review_link" and active is None:
            return self._rejected("ACTIVE_REVIEW_LINK_REQUIRED")

        actor = command["actor"]
        if action_id in {"send_review_request", "resend_review_request"}:
            if active is not None:
                active["status"] = "REVOKED"
            link = {
                "link_id": f"review-link-{self._next_link:03d}",
                "project_id": FIXTURE_PROJECT_ID,
                "version_id": FIXTURE_VERSION_ID,
                "recipient": FIXTURE_REVIEWER_EMAIL,
                "status": "ACTIVE",
                "validity_days": 30,
            }
            self._next_link += 1
            self._authoritative_state["review_links"].append(link)
            self._authoritative_state["active_review_link_id"] = link["link_id"]
            self._authoritative_state["review_link_revision"] += 1
            if action_id == "send_review_request":
                self._authoritative_state["version"]["status"] = "IN_REVIEW"
            event = "REVIEW_REQUEST_SENT" if action_id == "send_review_request" else "REVIEW_REQUEST_RESENT"
            effect = "REVIEW_LINK_CREATED" if action_id == "send_review_request" else "REVIEW_LINK_ROTATED"
            self._commit(
                action_id=action_id,
                actor=actor,
                history={"event": event, "link_id": link["link_id"]},
                business_effect={"effect": effect, "link_id": link["link_id"]},
                delivery_effect={
                    "effect": "REVIEW_EMAIL_SENT",
                    "recipient": FIXTURE_REVIEWER_EMAIL,
                    "link_id": link["link_id"],
                },
            )
            result = {
                "result_class": "SUCCESS",
                "review_link_revision": self._authoritative_state["review_link_revision"],
                "review_link": copy.deepcopy(link),
            }
        else:
            active["status"] = "REVOKED"
            self._authoritative_state["active_review_link_id"] = None
            self._authoritative_state["review_link_revision"] += 1
            self._commit(
                action_id=action_id,
                actor=actor,
                history={"event": "REVIEW_LINK_REVOKED", "link_id": active["link_id"]},
                business_effect={"effect": "REVIEW_LINK_REVOKED", "link_id": active["link_id"]},
            )
            result = {
                "result_class": "SUCCESS",
                "review_link_revision": self._authoritative_state["review_link_revision"],
                "revoked_review_link": copy.deepcopy(active),
                "notification_sent": False,
            }
        self._remember_attempt(action_id, command, result)
        return result


def _contract_actor(
    contract: dict[str, object],
    action_id: str,
    *,
    index: int | None = None,
) -> str:
    action = next(action for action in contract["actions"] if action["action_id"] == action_id)
    actor = action["fields"]["actor"]["value"]
    return actor[index] if index is not None else actor


def _pin_command(
    contract: dict[str, object],
    attempt_id: str,
    expected_state_revision: int,
) -> dict[str, object]:
    return {
        "action_id": "create_pin",
        "actor": _contract_actor(contract, "create_pin"),
        "project_id": FIXTURE_PROJECT_ID,
        "version_id": FIXTURE_VERSION_ID,
        "expected_state_revision": expected_state_revision,
        "message_attempt_id": attempt_id,
        "media_type": "IMAGE",
        "x": 0.25,
        "y": 0.75,
        "comment": "Fixture root comment.",
    }


def _thread_command(
    contract: dict[str, object],
    action_id: str,
    thread_id: str,
    attempt_id: str,
    expected_state_revision: int,
) -> dict[str, object]:
    command = {
        "action_id": action_id,
        "actor": _contract_actor(contract, action_id, index=0) if action_id == "reply_thread" else _contract_actor(contract, action_id),
        "project_id": FIXTURE_PROJECT_ID,
        "version_id": FIXTURE_VERSION_ID,
        "expected_state_revision": expected_state_revision,
        "thread_id": thread_id,
        "message_attempt_id": attempt_id,
    }
    if action_id == "reply_thread":
        command["message"] = "Fixture reply."
    return command


def _review_command(
    contract: dict[str, object],
    action_id: str,
    attempt_id: str,
    expected_revision: int,
) -> dict[str, object]:
    return {
        "action_id": action_id,
        "actor": _contract_actor(contract, action_id),
        "project_id": FIXTURE_PROJECT_ID,
        "version_id": FIXTURE_VERSION_ID,
        "recipient": FIXTURE_REVIEWER_EMAIL,
        "client_attempt_id": attempt_id,
        "expected_review_link_revision": expected_revision,
    }


def _setup_thread(
    fixture: ClientFeedbackPortalFixture,
    contract: dict[str, object],
) -> str:
    created = fixture.execute(_pin_command(contract, "setup-pin", 1))
    return created["result"]["thread_id"]


def _setup_review_link(
    fixture: ClientFeedbackPortalFixture,
    contract: dict[str, object],
) -> None:
    fixture.execute(_review_command(contract, "send_review_request", "setup-review-link", 0))


def execute_fixture_scenario(
    contract: dict[str, object],
    action_id: str,
    result_class: str,
) -> dict[str, object]:
    """Execute one deterministic planned case through the actual action handler."""
    permitted = {
        "create_pin": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
        "reply_thread": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
        "resolve_thread": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
        "send_review_request": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
        "resend_review_request": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
        "revoke_review_link": {"SUCCESS", "REJECTED", "STALE", "IDEMPOTENT_REPLAY"},
    }
    if action_id not in permitted or result_class not in permitted[action_id]:
        raise ValueError("UNSUPPORTED_FIXTURE_SCENARIO")
    fixture = ClientFeedbackPortalFixture(contract)

    if action_id == "create_pin":
        current_revision = fixture.snapshot()["authoritative_state"]["version"]["revision"]
        command = _pin_command(
            contract,
            f"target-{action_id}",
            current_revision - 1 if result_class == "STALE" else current_revision,
        )
    elif action_id in {"reply_thread", "resolve_thread"}:
        thread_id = _setup_thread(fixture, contract)
        current_revision = fixture.snapshot()["authoritative_state"]["version"]["revision"]
        command = _thread_command(
            contract,
            action_id,
            thread_id,
            f"target-{action_id}",
            current_revision - 1 if result_class == "STALE" else current_revision,
        )
    else:
        if action_id in {"resend_review_request", "revoke_review_link"} or result_class == "STALE":
            _setup_review_link(fixture, contract)
            expected_revision = 0 if result_class == "STALE" else 1
        else:
            expected_revision = 0
        command = _review_command(
            contract,
            action_id,
            f"target-{action_id}",
            expected_revision,
        )

    if result_class == "REJECTED":
        command["actor"] = "UNAUTHORIZED_FIXTURE_ACTOR"
        return fixture.execute(command)
    if result_class == "IDEMPOTENT_REPLAY":
        first = fixture.execute(command)
        if first["result"]["result_class"] != "SUCCESS":
            raise ValueError("FIXTURE_SCENARIO_SETUP_FAILED")
        return fixture.execute(command)
    execution = fixture.execute(command)
    if execution["result"].get("result_class") != result_class:
        raise ValueError("FIXTURE_SCENARIO_RESULT_MISMATCH")
    return execution


__all__ = [
    "ClientFeedbackPortalFixture",
    "FIXTURE_PROJECT_ID",
    "FIXTURE_REVIEWER_EMAIL",
    "FIXTURE_VERSION_ID",
    "execute_fixture_scenario",
]
