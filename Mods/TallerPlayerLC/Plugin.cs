using BepInEx;
using BepInEx.Configuration;
using HarmonyLib;
using UnityEngine;

namespace TallPlayerMod
{
    [BepInPlugin(PluginInfo.PLUGIN_GUID, PluginInfo.PLUGIN_NAME, PluginInfo.PLUGIN_VERSION)]
    public class Plugin : BaseUnityPlugin
    {
        private readonly Harmony harmony = new Harmony(PluginInfo.PLUGIN_GUID);
        private ConfigEntry<float> heightMultiplier;

        private void Awake()
        {
            // Create config option for height multiplier
            heightMultiplier = Config.Bind("General",
                "HeightMultiplier",
                1.5f,
                "How much taller to make the player (1.0 is normal height)");

            // Apply patches
            harmony.PatchAll();
            Logger.LogInfo($"Plugin {PluginInfo.PLUGIN_GUID} is loaded!");
        }

        [HarmonyPatch(typeof(StartOfRound), "Start")]
        class PlayerScalePatch
        {
            static void Postfix(StartOfRound __instance)
            {
                foreach (GameObject player in GameObject.FindGameObjectsWithTag("Player"))
                {
                    // Scale the player model
                    Vector3 newScale = player.transform.localScale;
                    newScale.y *= Plugin.Instance.heightMultiplier.Value;
                    player.transform.localScale = newScale;
                }
            }
        }

        public static Plugin Instance;

        private void Start()
        {
            Instance = this;
        }
    }
} 