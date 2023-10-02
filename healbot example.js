function HealBot()
    {
    var crossHealList = '0x009A9DFB|0x00D1BE62'; //other characters' serials
    var crossHealThreshold = 80; //percentage
    var selfHealThreshold = 80; //percentage
    var notoriety = 'blue|green'
    while(!Player.Dead())
        {
        var injuredList = Orion.FindTypeEx(any, any, ground, "ignoreself|mobile", 2, notoriety).filter(function(mob)
            { //create a list of mobiles whose serial number exists in crossHealList and hp less than threshold
            return crossHealList.indexOf(mob.Serial()) > -1 && mob.Hits('%') < crossHealThreshold;
            }).sort(function(a,b)
                { //sort the list from most injured to least
                return a.Hits() - b.Hits();
                });
        var bandies = Orion.FindType('0x0E21')[0];
        if(!bandies)
            {
            Orion.CharPrint(self,1159,'Out of bandies!');
            }
        else if(injuredList.length && !Orion.BuffExists('Healing Skill'))
            {
            var crossHealTarget = injuredList[0];
            Orion.UseObject(bandies);
            if(Orion.WaitForTarget(2000))
                Orion.TargetObject(target.Serial());
            }
        else if(Player.Hits('%') < selfHealThreshold && !Orion.BuffExists('Healing Skill'))
            {
            Orion.UseObject(bandies);
            if(Orion.WaitForTarget(2000))
                Orion.TargetObject(self);
            }
        Orion.Wait(250);
        }
    }

if(another injured player in range)
    {
    heal that player
    }
else if(Player.Hits('%') < 90)
    {
    heal self
    }