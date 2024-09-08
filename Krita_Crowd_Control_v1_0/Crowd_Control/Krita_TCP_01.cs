///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// The TCP game pack script for Crowd Control //


	// Most of this is copy pasted from the Crowd Control example, but there are a few things that need changing
	//		to get a working script from the example.


	// See https://developer.crowdcontrol.live/sdk/#creating-a-game-pack
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
using ConnectorLib.SimpleTCP;
using CrowdControl.Common;
using ConnectorType = CrowdControl.Common.ConnectorType;


namespace CrowdControl.Games.Packs.Krita;

public class Krita : SimpleTCPPack<SimpleTCPServerConnector>
{
	protected override string ProcessName => "Krita";

    public override string Host => "127.0.0.1";
    public override ushort Port => 2323;			// Anything between 1024 - 49151

    public Krita(	UserRecord player,
					Func<CrowdControlBlock, bool> responseHandler,
					Action<object> statusUpdateHandler) : base(player, responseHandler, statusUpdateHandler) { }

    public override Game Game => new("Krita", "Krita", "PC", ConnectorType.SimpleTCPServerConnector);



    public override EffectList Effects => new Effect[]
    {
		// Spin the canvas
        new("Spin Canvas", "spin_canvas") {	Price = 100,
											Duration = 10,
											Description = "Give the canvas a speeen",
											Category = "Canvas" },

		// Spin it slowly and chaotically
        new("Spin Slow Chaotic", "spin_slow_chaotic") {	Price = 100,
														Duration = 10,
														Description = "Give the canvas a slow chaotic speeen",
														Category = "Canvas" },

		// Nudge clockwise
		new("Nudge Clockwise", "nudge_canvas_cw") {	Price = 100,
													Description = "Nudge Clockwise",
													Category = "Canvas" },

		// Nudge counter clockwise
		new("Nudge Counter Clockwise", "nudge_canvas_ccw") {	Price = 100,
																Description = "Nudge Counter Clockwise",
																Category = "Canvas" },

		// Vertical flip
		new("Vertical Flip", "vertical_flip") {	Price = 100,
												Description = "Vertical Flip",
												Category = "Canvas" },

		// Horizontal flip
		new("Horizontal Flip", "horizontal_flip") {	Price = 100,
													Description = "Horizontal Flip",
													Category = "Canvas" },

		// Rainbow paint
        new("Rainbow Paint", "rainbow_paint") {	Price = 100,
												Description = "Rainbow paint!",
												Category = "Brush" }
    };
}