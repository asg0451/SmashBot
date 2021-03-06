import melee
import Chains
from melee.enums import Action, Character
from Tactics.tactic import Tactic

class Retreat(Tactic):
    def shouldretreat(smashbot_state, opponent_state):
        if smashbot_state.invulnerability_left > 1:
            return False

        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]

        winning = smashbot_state.stock > opponent_state.stock
        if smashbot_state.stock == opponent_state.stock and smashbot_state.percent < opponent_state.percent:
            winning = False

        if opponent_state.character == Character.SHEIK and opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            # If we're ahead, retreat from the chain
            if winning:
                return True

        # FireFox is different
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_3_LOW] \
            and opponent_state.character in [Character.FOX, Character.FALCO]
        if firefox:
            return True

        # If opponent is landing from an attack, and we're sheilding, retreat!
        if opponent_state.action in [Action.DAIR_LANDING, Action.NAIR_LANDING, Action.FAIR_LANDING, \
                Action.UAIR_LANDING, Action.BAIR_LANDING, Action.LANDING] and smashbot_state.action in shieldactions:
            return True

        # If opponent is falling, and we're in shield, retreat
        if opponent_state.speed_y_self < 0 and not opponent_state.on_ground and smashbot_state.action in shieldactions:
            return True

        if opponent_state.action == Action.LOOPING_ATTACK_MIDDLE:
            return True

        return False

    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        needswavedash = self.smashbot_state.action in [Action.DOWN_B_GROUND, Action.DOWN_B_STUN, \
            Action.DOWN_B_GROUND_START, Action.LANDING_SPECIAL, Action.SHIELD, Action.SHIELD_START, \
            Action.SHIELD_RELEASE, Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        if needswavedash:
            self.pickchain(Chains.Wavedash, [1, False])
            return

        bufferzone = 30
        if self.opponent_state.character == Character.SHEIK and self.opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            bufferzone = 55
        onright = self.opponent_state.x < self.smashbot_state.x
        if not onright:
            bufferzone *= -1

        pivotpoint = self.opponent_state.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        edgebuffer = 30
        edge = melee.stages.edgegroundposition(self.gamestate.stage) - edgebuffer
        # If we are about to pivot near the edge, just grab the edge instead
        if abs(pivotpoint) > edge:
            self.pickchain(Chains.Grabedge)
            return

        pivotpoint = min(pivotpoint, edge)
        pivotpoint = max(pivotpoint, -edge)

        self.chain = None
        self.pickchain(Chains.DashDance, [pivotpoint])
