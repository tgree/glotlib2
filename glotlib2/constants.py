MOUSE_BUTTON_LEFT   = 0
MOUSE_BUTTON_RIGHT  = 1
MOUSE_BUTTON_MIDDLE = 2

MOUSE_BUTTON_PRESS   = 1
MOUSE_BUTTON_RELEASE = 2

ASPECT_NONE     = 0
ASPECT_SQUARE   = 1

KEY_PRESS   = 1
KEY_RELEASE = 2

# Key codes used in press/release handlers.  For most characters we use their
# ASCII values and they are not defined here - these are for special keys that
# don't have ASCII equivalents.
KEY_CAPS_LOCK       = 256
KEY_DELETE          = 257
KEY_DOWN_ARROW      = 258
KEY_END             = 259
KEY_ESCAPE          = chr(27)
KEY_F1              = 260
KEY_F2              = 261
KEY_F3              = 262
KEY_F4              = 263
KEY_F5              = 264
KEY_F6              = 265
KEY_F7              = 266
KEY_F8              = 267
KEY_F9              = 268
KEY_F10             = 269
KEY_F11             = 270
KEY_F12             = 271
KEY_F13             = 272
KEY_F14             = 273
KEY_F15             = 274
KEY_F16             = 275
KEY_F17             = 276
KEY_F18             = 277
KEY_F19             = 278
KEY_F20             = 279
KEY_F21             = 280
KEY_F22             = 281
KEY_F23             = 282
KEY_F24             = 283
KEY_F25             = 284
KEY_HOME            = 285
KEY_INSERT          = 286
KEYPAD_0            = 287
KEYPAD_1            = 288
KEYPAD_2            = 289
KEYPAD_3            = 290
KEYPAD_4            = 291
KEYPAD_5            = 292
KEYPAD_6            = 293
KEYPAD_7            = 294
KEYPAD_8            = 295
KEYPAD_9            = 296
KEYPAD_PLUS         = 297
KEYPAD_DOT          = 298
KEYPAD_DIVIDE       = 299
KEYPAD_ENTER        = 300
KEYPAD_EQUALS       = 301
KEYPAD_MULTIPLY     = 302
KEYPAD_MINUS        = 303
KEY_LEFT_ARROW      = 304
KEY_LEFT_ALT        = 305
KEY_LEFT_CONTROL    = 306
KEY_LEFT_SHIFT      = 307
KEY_LEFT_SUPER      = 308
KEY_MENU            = 309
KEY_NUM_LOCK        = 310
KEY_PAGE_DOWN       = 311
KEY_PAGE_UP         = 312
KEY_PAUSE           = 313
KEY_PRINT_SCREEN    = 314
KEY_RIGHT_ARROW     = 315
KEY_RIGHT_ALT       = 316
KEY_RIGHT_CONTROL   = 317
KEY_RIGHT_SHIFT     = 318
KEY_RIGHT_SUPER     = 319
KEY_SCROLL_LOCK     = 320
KEY_UP_ARROW        = 321

# Modifier bitmask used in other handlers.
MOD_LEFT_SHIFT    = (1 << 0)
MOD_RIGHT_SHIFT   = (1 << 1)
MOD_LEFT_ALT      = (1 << 2)
MOD_RIGHT_ALT     = (1 << 3)
MOD_LEFT_CONTROL  = (1 << 4)
MOD_RIGHT_CONTROL = (1 << 5)
MOD_ANY_SHIFT     = MOD_LEFT_SHIFT | MOD_RIGHT_SHIFT
MOD_ANY_ALT       = MOD_LEFT_ALT | MOD_RIGHT_ALT
MOD_ANY_CONTROL   = MOD_LEFT_CONTROL | MOD_RIGHT_CONTROL

KEY_TO_MODIFIER_MAP = {
    KEY_LEFT_SHIFT      : MOD_LEFT_SHIFT,
    KEY_RIGHT_SHIFT     : MOD_RIGHT_SHIFT,
    KEY_LEFT_ALT        : MOD_LEFT_ALT,
    KEY_RIGHT_ALT       : MOD_RIGHT_ALT,
    KEY_LEFT_CONTROL    : MOD_LEFT_CONTROL,
    KEY_RIGHT_CONTROL   : MOD_RIGHT_CONTROL,
}
