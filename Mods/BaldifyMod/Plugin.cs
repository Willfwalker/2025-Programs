using BepInEx;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;
using UnityEngine;
using GameNetcodeStuff;

namespace BaldifyMod
{
    [BepInPlugin(MyPluginInfo.PLUGIN_GUID, MyPluginInfo.PLUGIN_NAME, MyPluginInfo.PLUGIN_VERSION)]
    public class Plugin : BasePlugin
    {
        public override void Load()
        {
            // Plugin startup logic
            Log.LogInfo($"Plugin {MyPluginInfo.PLUGIN_GUID} is loaded!");
            
            // Apply Harmony patches
            Harmony.CreateAndPatchAll(typeof(Plugin));
        }

        private void Update()
        {
            // Check if the equals key is pressed
            if (Input.GetKeyDown(KeyCode.Equals))
            {
                // Get the local player
                PlayerControllerB localPlayer = StartOfRound.Instance.localPlayerController;
                
                // Perform raycast from player's view
                Ray ray = new Ray(localPlayer.gameplayCamera.transform.position, localPlayer.gameplayCamera.transform.forward);
                RaycastHit hit;
                
                if (Physics.Raycast(ray, out hit, 10f))
                {
                    // Check if we hit another player
                    PlayerControllerB targetPlayer = hit.collider.GetComponent<PlayerControllerB>();
                    if (targetPlayer != null)
                    {
                        // Make the player bald by disabling their hair mesh
                        Transform hairTransform = targetPlayer.transform.Find("PlayerModel/Hair");
                        if (hairTransform != null)
                        {
                            hairTransform.gameObject.SetActive(false);
                        }
                    }
                }
            }
        }
    }
} 