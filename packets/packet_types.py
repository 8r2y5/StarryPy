from construct import *
from enum import IntEnum
from data_types import SignedVLQ, VLQ, Variant, star_string, DictVariant, StarByteArray


class Direction(IntEnum):
    CLIENT = 0
    SERVER = 1


class Packets(IntEnum):
    PROTOCOL_VERSION = 0
    SERVER_DISCONNECT = 1
    CONNECT_RESPONSE = 2
    HANDSHAKE_CHALLENGE = 3
    CHAT_RECEIVED = 4
    UNIVERSE_TIME_UPDATE = 5
    CELESTIAL_RESPONSE = 6
    CLIENT_CONNECT = 7
    CLIENT_DISCONNECT_REQUEST = 8
    HANDSHAKE_RESPONSE = 9
    PLAYER_WARP = 10
    FLY_SHIP = 11
    CHAT_SENT = 12
    CELESTIAL_REQUEST = 13
    CLIENT_CONTEXT_UPDATE = 14
    WORLD_START = 15
    WORLD_STOP = 16
    CENTRAL_STRUCTURE_UPDATE = 17
    TILE_ARRAY_UPDATE = 18
    TILE_UPDATE = 19
    TILE_LIQUID_UPDATE = 20
    TILE_DAMAGE_UPDATE = 21
    TILE_MODIFICATION_FAILURE = 22
    GIVE_ITEM = 23
    SWAP_IN_CONTAINER_RESULT = 24
    ENVIRONMENT_UPDATE = 25
    ENTITY_INTERACT_RESULT = 26
    UPDATE_TILE_PROTECTION = 27
    MODIFY_TILE_LIST = 28
    DAMAGE_TILE_GROUP = 29
    COLLECT_LIQUID = 30
    REQUEST_DROP = 31
    SPAWN_ENTITY = 32
    ENTITY_INTERACT = 33
    CONNECT_WIRE = 34
    DISCONNECT_ALL_WIRES = 35
    OPEN_CONTAINER = 36
    CLOSE_CONTAINER = 37
    SWAP_IN_CONTAINER = 38
    ITEM_APPLY_IN_CONTAINER = 39
    START_CRAFTING_IN_CONTAINER = 40
    STOP_CRAFTING_IN_CONTAINER = 41
    BURN_CONTAINER = 42
    CLEAR_CONTAINER = 43
    WORLD_CLIENT_STATE_UPDATE = 44
    ENTITY_CREATE = 45
    ENTITY_UPDATE = 46
    ENTITY_DESTROY = 47
    HIT_REQUEST = 48
    DAMAGE_REQUEST = 49
    DAMAGE_NOTIFICATION = 50
    CALL_SCRIPTED_ENTITY = 51
    UPDATE_WORLD_PROPERTIES = 52
    HEARTBEAT = 53


class EntityType(IntEnum):
    END = -1
    PLAYER = 0
    MONSTER = 1
    OBJECT = 2
    ITEMDROP = 3
    PROJECTILE = 4
    PLANT = 5
    PLANTDROP = 6
    EFFECT = 7
    NPC = 8


class MessageContextMode(IntEnum):
    CHANNEL = 1
    BROADCAST = 2
    WHISPER = 3
    COMMAND_RESULT = 4


class PacketOutOfOrder(Exception):
    pass


class HexAdapter(Adapter):
    def _encode(self, obj, context):
        return obj.decode(
            "hex")  # The code seems backward, but I assure you it's correct.

    def _decode(self, obj, context):
        return obj.encode("hex")


# may need to be corrected. new version only has hash, uses ByteArray
handshake_response = lambda name="handshake_response": Struct(name,
                                                              star_string("claim_response"),
                                                              star_string("hash"))

# small correction. added proper context. may need to check if this is correct (need double. used bfloat64).
universe_time_update = lambda name="universe_time": Struct(name,
                                                           #VLQ("unknown"))
                                                           BFloat64("universe_time"))

packet = lambda name="base_packet": Struct(name,
                                           Byte("id"),
                                           SignedVLQ("payload_size"),
                                           Field("data", lambda ctx: abs(
                                               ctx.payload_size)))

start_packet = lambda name="interim_packet": Struct(name,
                                                    Byte("id"),
                                                    SignedVLQ("payload_size"))

# should still work. nothing's changed here.
protocol_version = lambda name="protocol_version": Struct(name,
                                                          UBInt32("server_build"))

connection = lambda name="connection": Struct(name,
                                              GreedyRange(Byte("compressed_data")))

# may need to be corrected. new version only has salt, uses ByteArray
handshake_challenge = lambda name="handshake_challenge": Struct(name,
                                                                star_string("claim_message"),
                                                                star_string("salt"),
                                                                SBInt32("round_count"))

# Needs attention
connect_response = lambda name="connect_response": Struct(name,
                                                          Flag("success"),
                                                          VLQ("client_id"),
                                                          star_string("reject_reason")
                                                          # may need to add something here CelestialBaseInformation
                                                          )

# corrected. needs testing
chat_received = lambda name="chat_received": Struct(name,
                                                    Struct("message_context",
                                                           Byte("mode"),
                                                           If(lambda ctx: ctx.mode is True,
                                                              star_string("chat_channel")
                                                           )
                                                    ),
                                                    UBInt32("client_id"),
                                                    star_string("name"),
                                                    star_string("message"))

# corrected. shouldn't need too much testing
chat_sent = lambda name="chat_sent": Struct(name,
                                            star_string("message"),
                                            Enum(Byte("send_mode"),
                                                 BROADCAST=1,
                                                 LOCAL=2,
                                                 PARTY=3)
                                            )

# quite a bit of guesswork and hackery here with the ship_upgrades.
client_connect = lambda name="client_connect": Struct(name,
                                                      VLQ("asset_digest_length"),
                                                      String("asset_digest",
                                                             lambda ctx: ctx.asset_digest_length),
                                                      #Variant("claim"), # no longer used?
                                                      Flag("uuid_exists"),
                                                      If(lambda ctx: ctx.uuid_exists is True,
                                                         HexAdapter(Field("uuid", 16))
                                                      ),
                                                      star_string("name"),
                                                      star_string("species"),
                                                      #VLQ("shipworld_length"),
                                                      #Field("shipworld", lambda ctx: ctx.shipworld_length),
                                                      StarByteArray("ship_data"),
                                                      # Replace: ShipUpgrades
                                                      Struct("ship_upgrades",
                                                             UBInt32("ship_level"),
                                                             UBInt32("max_fuel"),
                                                             VLQ("capabilities")),
                                                      star_string("account"))

client_disconnect = lambda name="client_disconnect": Struct(name,
                                                            Byte("data"))

world_coordinate = lambda name="world_coordinate": Struct(name,
                                                          star_string("sector"),
                                                          SBInt32("x"),
                                                          SBInt32("y"),
                                                          SBInt32("z"),
                                                          SBInt32("planet"),
                                                          SBInt32("satellite"))

warp_command = lambda name="warp_command": Struct(name,
                                                  Enum(UBInt32("warp_type"),
                                                       MOVE_SHIP=1,
                                                       WARP_UP=2,
                                                       WARP_OTHER_SHIP=3,
                                                       WARP_DOWN=4,
                                                       WARP_HOME=5),
                                                  world_coordinate(),
                                                  star_string("player"))

warp_command_write = lambda t, sector=u'', x=0, y=0, z=0, planet=0, satellite=0, player=u'': warp_command().build(
    Container(
        warp_type=t,
        world_coordinate=Container(
            sector=sector,
            x=x,
            y=y,
            z=z,
            planet=planet,
            satellite=satellite
        ),
        player=player))


# partially correct. Needs work on dungeon ID value
world_start = lambda name="world_start": Struct(name,
                                                Variant("planet"), # rename to templateData?
                                                #Variant("world_structure"),
                                                StarByteArray("sky_structure"),
                                                StarByteArray("weather_data"),
                                                #BFloat32("spawn_x"),
                                                #BFloat32("spawn_y"),
                                                Array(2, BFloat32("coordinate")),
                                                Variant("world_properties"),
                                                UBInt32("client_id"),
                                                Flag("local_interpolation"))

world_stop = lambda name="world_stop": Struct(name,
                                              star_string("status"))

# I THINK this is ok. Will test later.
give_item = lambda name="give_item": Struct(name,
                                            star_string("name"),
                                            VLQ("count"),
                                            Byte("variant_type"),
                                            star_string("description"))

give_item_write = lambda name, count: give_item().build(Container(name=name,
                                                                  count=count,
                                                                  variant_type=7,
                                                                  description=''))

# replaced with something closer matched to SB documentation
update_world_properties = lambda name="world_properties": Struct(name,
                                                                 DictVariant("updated_properties"))
#update_world_properties = lambda name="world_properties": Struct(name,
#                                                                 UBInt8("count"),
#                                                                 Array(lambda ctx: ctx.count,
#                                                                       Struct("properties",
#                                                                              star_string("key"),
#                                                                              Variant("value"))))

update_world_properties_write = lambda dictionary: update_world_properties().build(
    Container(
        count=len(dictionary),
        properties=[Container(key=k, value=Container(type="SVLQ", data=v)) for k, v in dictionary.items()]))

entity_create = Struct("entity_create",
                       GreedyRange(
                           Struct("entity",
                                  Byte("entity_type"),
                                  VLQ("entity_size"),
                                  String("entity", lambda ctx: ctx.entity_size),
                                  SignedVLQ("entity_id"))))

# replaced with something closer matched to SB documentation
client_context_update = lambda name="client_context": Struct(name,
                                                             StarByteArray("update_data"))
#client_context_update = lambda name="client_context": Struct(name,
#                                                             VLQ("length"),
#                                                             Byte("arguments"),
#                                                             Array(lambda ctx: ctx.arguments,
#                                                                   Struct("key",
#                                                                   Variant("value"))))

projectile = DictVariant("projectile")
